#!/usr/bin/env python3
"""Tech Radar — Audio Production v7
Pipeline: parse script → shared fixed assets → TTS (edge-tts) → merge MP3
Supports multiple guests: [GUEST] or [GUEST_1], [GUEST_2], ... in script.
"""

import os, re, json, time, shutil, datetime, subprocess, sys, argparse, threading, hashlib
from pathlib import Path
from pydub import AudioSegment
from concurrent.futures import ThreadPoolExecutor, as_completed

def _preparse_workspace(argv: list[str]) -> Path:
    workspace = os.environ.get("PODCAST_WORKSPACE", "").strip()
    if workspace:
        return Path(workspace).expanduser().resolve()
    for i, token in enumerate(argv):
        if token == "--workspace" and i + 1 < len(argv):
            return Path(argv[i + 1]).expanduser().resolve()
        if token.startswith("--workspace="):
            return Path(token.split("=", 1)[1]).expanduser().resolve()
    return Path.cwd().resolve()


BASE       = _preparse_workspace(sys.argv[1:])
CACHE_DIR  = BASE / "cache"
SEGS_DIR   = CACHE_DIR / "segments"
LOGS_DIR   = BASE / "logs"
EXPORTS_DIR = BASE / "exports"
SUPPRESS_INIT_OUTPUT = any(flag in sys.argv[1:] for flag in ("-h", "--help"))
for d in [CACHE_DIR, SEGS_DIR, LOGS_DIR, EXPORTS_DIR]:
    d.mkdir(exist_ok=True)

# ── Config loading ───────────────────────────────────────────────────────────

def find_config() -> dict:
    """Search for voice_config.json — walks up from episode folder, then checks home."""
    skill_rels = [
        ".agents/skills/tech-radar-podcast/assets/voice_config.json",
        ".claude/skills/tech-radar-podcast/assets/voice_config.json",
    ]
    ancestors = [Path(__file__).parent / "assets" / "voice_config.json"]
    p = Path(__file__).parent
    for _ in range(8):
        p = p.parent
        for rel in skill_rels:
            ancestors.append(p / rel)
    for rel in skill_rels:
        ancestors.append(Path.home() / rel)
    for candidate in ancestors:
        if candidate.exists():
            return json.loads(candidate.read_text())
    return {}


def find_assets_dir() -> Path | None:
    """Search for the skill assets directory containing fixed audio files."""
    skill_rels = [
        ".agents/skills/tech-radar-podcast/assets",
        ".claude/skills/tech-radar-podcast/assets",
    ]
    p = Path(__file__).parent
    for _ in range(8):
        for rel in skill_rels:
            candidate = p / rel
            if candidate.exists():
                return candidate
        p = p.parent
    for rel in skill_rels:
        candidate = Path.home() / rel
        if candidate.exists():
            return candidate
    return None


# ── Configuration & Rules ─────────────────────────────────────────────────────
CONFIG    = find_config()
AUDIO_CFG = CONFIG.get("audio", {})
PHONETIC  = CONFIG.get("phonetic_normalization", {})
POLISH_CFG = CONFIG.get("tts_polish", {})
ASSETS_DIR = find_assets_dir()
SEGMENT_TITLE_CFG = AUDIO_CFG.get("segment_title_announcement", {})
LOUDNESS_CFG = AUDIO_CFG.get("loudness_normalization", {})
PAUSE_RULES = AUDIO_CFG.get("pause_rules", {})
OUTPUT_BITRATE = AUDIO_CFG.get("bitrate", "128k")
PLAYBACK_SPEED = float(AUDIO_CFG.get("playback_speed", 1.0))
PLAYBACK_SPEED_BY_LANGUAGE = AUDIO_CFG.get("playback_speed_by_language", {})
RUN_BENCHMARK = os.environ.get("PODCAST_BENCHMARK", "").strip().lower() in {"1", "true", "yes"}
BENCHMARK_RECORDS: list[dict] = []
BENCH_LOCK = threading.Lock()

STATUS_PATH = BASE / "status.json"
WORKSPACE_MANIFEST_PATH = BASE / "workspace_manifest.json"
PHASE_EVENTS_PATH = LOGS_DIR / "phase_events.jsonl"

def _find_binary(name: str) -> str | None:
    path = shutil.which(name)
    if path:
        return path
    fallback = Path("/opt/homebrew/bin") / name
    if fallback.exists():
        return str(fallback)
    return None


FFMPEG_BIN = _find_binary("ffmpeg") or "ffmpeg"
FFPROBE_BIN = _find_binary("ffprobe")
EDGE_TTS_BIN = _find_binary("edge-tts")


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def append_phase_event(phase: str, status: str, details: dict | None = None) -> None:
    event = {
        "time": datetime.datetime.now().isoformat(timespec="seconds"),
        "phase": phase,
        "status": status,
    }
    if details:
        event["details"] = details
    with PHASE_EVENTS_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")


def sync_status_markdown(status_data: dict) -> None:
    status_md = BASE / "STATUS.md"
    lines = [f"# {BASE.name} Status", ""]
    phases = status_data.get("phases", {})
    for phase in ("initialized", "research", "outline", "script_en", "script_vi", "audio_render"):
        info = phases.get(phase, {})
        marker = "x" if info.get("status") == "completed" else " "
        lines.append(f"- [{marker}] {phase}")
    lines.append("")
    lines.append(f"Current phase: `{status_data.get('current_phase', '')}`")
    lines.append(f"Updated: `{status_data.get('updated_at', '')}`")
    status_md.write_text("\n".join(lines) + "\n")


def update_status(phase: str, status: str, details: dict | None = None) -> None:
    data = _read_json(STATUS_PATH)
    phases = data.get("phases", {})
    if not isinstance(phases, dict):
        phases = {}
    phases[phase] = {
        "status": status,
        "updated_at": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    if details:
        phases[phase]["details"] = details
    data["workspace"] = str(BASE)
    data["current_phase"] = phase
    data["updated_at"] = datetime.datetime.now().isoformat(timespec="seconds")
    data["phases"] = phases
    _write_json(STATUS_PATH, data)
    sync_status_markdown(data)
    append_phase_event(phase, status, details)


def detect_script_language(path: Path) -> str:
    """Heuristic language detection for provider auto-routing."""
    if not path.exists():
        return "vi"
    spoken = [
        line for line in path.read_text().splitlines()
        if re.match(r"^\[(?:HOST|GUEST(?:_\d+)?)\]", line)
    ]
    joined = "\n".join(spoken).strip()
    if not joined:
        return "vi"

    vi_diacritics = len(re.findall(r"[ăâđêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ]", joined, re.IGNORECASE))
    en_hits = len(re.findall(r"\b(the|and|is|are|for|with|from|to|of|you|we|this|that|what|why|how)\b", joined, re.IGNORECASE))
    if vi_diacritics >= 6:
        return "vi"
    if en_hits >= 4:
        return "en"
    return "vi"


def detect_episode_language(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        data = json.loads(path.read_text())
    except Exception:
        return ""
    lang = (str(data.get("language") or data.get("lang") or "")).strip().lower()
    if lang in {"en", "vi"}:
        return lang
    return ""


def count_spoken_words(segments: list[dict]) -> int:
    total = 0
    for seg in segments:
        if seg.get("type") != "speech":
            continue
        text = seg.get("text", "")
        words = re.findall(r"[\wÀ-ỹ]+", text, flags=re.UNICODE)
        total += len(words)
    return total


def projected_minutes_from_words(spoken_words: int, lang: str, playback_speed: float) -> dict:
    # Conservative pace model to reduce under-estimation risk
    if lang == "vi":
        base_wpm = {"slow": 110, "medium": 140, "fast": 170}
    else:
        base_wpm = {"slow": 130, "medium": 160, "fast": 190}
    proj = {}
    for pace, wpm in base_wpm.items():
        eff = max(1.0, wpm * max(0.1, playback_speed))
        proj[pace] = round(spoken_words / eff, 2)
    return proj


def enforce_duration_guardrails(segments: list[dict], episode: dict, lang: str) -> None:
    if os.environ.get("PODCAST_SKIP_DURATION_GUARD", "").strip().lower() in {"1", "true", "yes"}:
        print("  Duration guardrail skipped via PODCAST_SKIP_DURATION_GUARD")
        return

    target = float(episode.get("duration_target_minutes") or 0)
    spoken_words = count_spoken_words(segments)
    proj = projected_minutes_from_words(spoken_words, lang, TARGET_PLAYBACK_SPEED)
    print(f"  Duration projection ({lang}): words={spoken_words} | slow={proj['slow']}m medium={proj['medium']}m fast={proj['fast']}m")

    if lang == "vi" and 29 <= target <= 31:
        min_words = 5400
        if spoken_words < min_words:
            raise SystemExit(
                f"Duration guard failed: VI 30-minute target requires >= {min_words} spoken words; got {spoken_words}. "
                "Append more script content before rendering."
            )

    if target > 0:
        required = round(target * 1.08, 2)
        # Use medium pace as principal projection
        if proj["medium"] < required:
            raise SystemExit(
                f"Duration guard failed: projected medium pace {proj['medium']}m < required safety {required}m "
                f"(target {target}m). Append one more script chunk and retry."
            )

def normalize_text(text: str, lang: str = "") -> str:
    """Apply phonetic replacement rules for tech terms and acronyms (Vietnamese only)."""
    effective_lang = lang or SCRIPT_LANGUAGE
    if effective_lang != "vi":
        return text
    if not text or not PHONETIC:
        return text
    fixed = text
    # Apply replacements using regex for word boundaries
    import re
    for key, val in PHONETIC.items():
        # Escape key for regex safety
        p = re.escape(key)
        # Use \b for whole words if key is alphanumeric
        pattern = fr"\b{p}\b" if key[0].isalnum() else p
        # Case-insensitive matching makes the same normalization work across
        # different script styles and capitalization choices.
        fixed = re.sub(pattern, val, fixed, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", fixed).strip()


def _domain_matches(topic: str, keywords: list[str]) -> bool:
    topic_lower = topic.lower()
    return any(keyword.lower() in topic_lower for keyword in keywords)


def _replace_phrases(text: str, replacements: dict[str, str]) -> str:
    fixed = text
    for src, dst in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
        fixed = re.sub(re.escape(src), dst, fixed, flags=re.IGNORECASE)
    return fixed


def polish_text(text: str, topic: str = "") -> str:
    """Convert risky written-tech phrasing into more speakable Vietnamese."""
    if not text or not POLISH_CFG.get("enabled", True):
        return text

    fixed = text
    fixed = re.sub(r"(\d+(?:[.,]\d+)?)\s*%", r"\1 phần trăm", fixed)
    fixed = re.sub(r"(\d+(?:[.,]\d+)?)\s*tỷ USD\b", r"\1 tỷ đô la Mỹ", fixed)
    fixed = re.sub(r"(\d+(?:[.,]\d+)?)\s*triệu USD\b", r"\1 triệu đô la Mỹ", fixed)
    fixed = re.sub(r"\bUSD\b", "đô la Mỹ", fixed)

    general = POLISH_CFG.get("general_replacements", {})
    if isinstance(general, dict):
        fixed = _replace_phrases(fixed, general)

    for domain_cfg in POLISH_CFG.get("domains", {}).values():
        if not isinstance(domain_cfg, dict):
            continue
        keywords = domain_cfg.get("keywords", [])
        replacements = domain_cfg.get("replacements", {})
        if _domain_matches(topic, keywords) and isinstance(replacements, dict):
            fixed = _replace_phrases(fixed, replacements)

    fixed = re.sub(r"\s+", " ", fixed).strip()
    return fixed


# ── TTS provider (edge-tts only) ─────────────────────────────────────────────

TTS_PROVIDER = "edge_tts"
SCRIPT_LANGUAGE = (
    (os.environ.get("PODCAST_LANG") or "").strip().lower()
    or detect_episode_language(BASE / "episode.json")
)
if SCRIPT_LANGUAGE not in {"vi", "en"}:
    SCRIPT_LANGUAGE = "vi"


def resolve_script_path(base: Path, lang: str) -> Path:
    """Pick the right script file based on language, with fallbacks."""
    lang_file = base / f"script_{lang}.txt"
    if lang_file.exists():
        return lang_file
    other = "en" if lang == "vi" else "vi"
    other_file = base / f"script_{other}.txt"
    if other_file.exists():
        return other_file
    legacy = base / "script.md"
    if legacy.exists():
        return legacy
    return lang_file

GAP_TURN    = AUDIO_CFG.get("gap_turn_ms", 400)
GAP_SEGMENT = AUDIO_CFG.get("gap_segment_ms", 1200)
GAP_MUSIC   = AUDIO_CFG.get("gap_music_ms", 2000)
GAP_SFX     = AUDIO_CFG.get("gap_sfx_ms", 800)
ANNOUNCE_SEGMENT_TITLES = SEGMENT_TITLE_CFG.get("enabled", True)
SEGMENT_TITLE_SPEAKER   = SEGMENT_TITLE_CFG.get("speaker", "HOST")
SEGMENT_TITLE_PROFILE   = SEGMENT_TITLE_CFG.get("tts_profile", "")
def _has_vietnamese(text: str) -> bool:
    """Check if text contains Vietnamese diacritical characters."""
    return bool(re.search(r"[ăâđêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ]", text, re.IGNORECASE))

def _resolve_template(cfg_value, lang: str, fallback_vi: str, fallback_en: str) -> str:
    """Resolve a template that may be a plain string or a {lang: text} dict."""
    if isinstance(cfg_value, dict):
        return cfg_value.get(lang) or cfg_value.get("en", fallback_en)
    # Plain string: use it if it matches the target language, otherwise fallback
    if not cfg_value:
        return fallback_vi if lang == "vi" else fallback_en
    if lang == "vi":
        return cfg_value
    # For non-vi: use the config value only if it's not Vietnamese
    if _has_vietnamese(cfg_value):
        return fallback_en
    return cfg_value

SEGMENT_TITLE_TEMPLATE = _resolve_template(
    SEGMENT_TITLE_CFG.get("template", ""),
    SCRIPT_LANGUAGE,
    fallback_vi="Phần tiếp theo, {title}.",
    fallback_en="Now, let's move on to {title}.",
)
SEGMENT_CLOSING_TEMPLATE = _resolve_template(
    SEGMENT_TITLE_CFG.get("closing_template", ""),
    SCRIPT_LANGUAGE,
    fallback_vi="Trước khi khép lại, chúng ta đến với {title}.",
    fallback_en="Before we wrap up, let's get to {title}.",
)



# ── Episode data ──────────────────────────────────────────────────────────────

def load_episode() -> dict:
    """Read episode.json written by Phase 1. Prioritizes Current Working Directory."""
    ep_file = BASE / "episode.json"
    if not ep_file.exists():
        ep_file = Path(__file__).parent / "episode.json"

    if ep_file.exists():
        try:
            return json.loads(ep_file.read_text())
        except Exception:
            pass
    return {}


def episode_guests(ep: dict) -> list[dict]:
    """Return list of guest dicts. Supports new (guests[]) and legacy (guest_name) formats."""
    if "guests" in ep:
        return ep["guests"]
    name = ep.get("guest_name", "")
    role = ep.get("guest_role", "")
    if name or role:
        return [{"name": name, "role": role}]
    return [{}]  # one anonymous guest slot so audio still runs


# ── Voice resolution ──────────────────────────────────────────────────────────

def _clean_hint_tokens(value) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, (list, tuple, set)):
        tokens = [str(v) for v in value]
    else:
        tokens = re.split(r"[,/|]", str(value))
    cleaned = {
        re.sub(r"[^a-z0-9]+", "_", token.strip().lower()).strip("_")
        for token in tokens
        if str(token).strip()
    }
    return {token for token in cleaned if token}


def _speaker_hint_values(ep: dict, guest: dict) -> dict[str, set[str]]:
    episode_style = ep.get("voice_style", {})
    guest_style = guest.get("voice_style", {})
    return {
        "gender": _clean_hint_tokens(
            guest.get("gender")
            or guest_style.get("gender")
            or episode_style.get("gender")
        ),
        "region": _clean_hint_tokens(
            guest.get("region")
            or guest.get("accent")
            or guest.get("dialect")
            or guest_style.get("region")
            or episode_style.get("region")
        ),
        "pace": _clean_hint_tokens(
            guest.get("pace")
            or guest.get("tempo")
            or guest_style.get("pace")
            or episode_style.get("pace")
        ),
        "energy": _clean_hint_tokens(
            guest.get("energy")
            or guest_style.get("energy")
            or episode_style.get("energy")
        ),
        "style": _clean_hint_tokens(
            guest.get("style")
            or guest.get("persona")
            or guest_style.get("style")
            or episode_style.get("style")
            or ep.get("tone")
        ),
    }


def _score_profile(profile: dict, topic: str, hints: dict[str, set[str]]) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []
    topic_lower = topic.lower()

    topic_hits = [kw for kw in profile.get("best_for_topics", []) if kw.lower() in topic_lower]
    if topic_hits:
        score += len(topic_hits) * 3
        reasons.append(f"topic:{', '.join(topic_hits[:2])}")

    profile_region = _clean_hint_tokens(profile.get("region"))
    profile_pace = _clean_hint_tokens(profile.get("pace"))
    profile_energy = _clean_hint_tokens(profile.get("energy"))
    profile_gender = _clean_hint_tokens(profile.get("gender"))
    profile_styles = _clean_hint_tokens(profile.get("best_for_styles", []))

    if hints["gender"]:
        if profile_gender & hints["gender"]:
            score += 8
            reasons.append(f"gender:{next(iter(profile_gender & hints['gender']))}")
        else:
            score -= 100
            reasons.append("gender_mismatch")

    if hints["region"] and profile_region & hints["region"]:
        score += 4
        reasons.append(f"region:{next(iter(profile_region & hints['region']))}")
    if hints["pace"] and profile_pace & hints["pace"]:
        score += 3
        reasons.append(f"pace:{next(iter(profile_pace & hints['pace']))}")
    if hints["energy"] and profile_energy & hints["energy"]:
        score += 2
        reasons.append(f"energy:{next(iter(profile_energy & hints['energy']))}")
    if hints["style"] and profile_styles & hints["style"]:
        score += 3
        reasons.append(f"style:{next(iter(profile_styles & hints['style']))}")

    return score, reasons


def _auto_select_profile(profiles: list[dict], topic: str, hints: dict[str, set[str]]) -> tuple[dict | None, str]:
    """Pick the best voice profile using topic, pace, region, and style hints."""
    if not profiles:
        return None, ""

    scored: list[tuple[int, dict, list[str]]] = []
    for profile in profiles:
        score, reasons = _score_profile(profile, topic, hints)
        scored.append((score, profile, reasons))

    best_score, best, reasons = max(scored, key=lambda item: item[0])
    if best_score <= 0:
        return None, ""

    reason_text = ", ".join(reasons) if reasons else "heuristic"
    return best, f"auto ({reason_text})"


def _record_benchmark(record: dict) -> None:
    if not RUN_BENCHMARK:
        return
    with BENCH_LOCK:
        BENCHMARK_RECORDS.append(record)


def resolve_all_voices(ep: dict) -> dict[str, dict]:
    """Returns {SPEAKER: voice_info} for HOST and all GUESTs."""
    guests   = episode_guests(ep)
    topic    = ep.get("topic", "")
    profiles = CONFIG.get("guest_voices", [])
    voices: dict[str, dict] = {}

    # ── HOST ──
    host_cfg = CONFIG.get("host", {})
    voices["HOST"] = {
        "voice_id":         os.environ.get("HOST_VOICE_ID") or host_cfg.get("voice_id", "vi-VN-NamMinhNeural"),
        "name":             host_cfg.get("name", "Trung"),
        "selection_method": "config",
    }

    # ── GUESTs ──
    used_profile_ids: set[str] = set()
    for i, guest in enumerate(guests):
        speaker = "GUEST" if i == 0 else f"GUEST_{i + 1}"
        env_vid = "GUEST_VOICE_ID" if i == 0 else f"GUEST_{i+1}_VOICE_ID"

        override_id = os.environ.get(env_vid, "")
        if override_id:
            voices[speaker] = {
                "voice_id": override_id,
                "name": guest.get("name", f"Guest {i + 1}"),
                "selection_method": f"env:{env_vid}",
            }
            continue

        # Profile selection: explicit > topic auto-select > first unused > first overall
        profile, method = None, ""
        hints = _speaker_hint_values(ep, guest)
        explicit = guest.get("voice_profile", "")
        if explicit and explicit != "auto":
            profile = next((p for p in profiles if p.get("id") == explicit), None)
            if profile:
                method = f"explicit:{explicit}"

        if not profile and topic:
            available = [p for p in profiles if p.get("id") not in used_profile_ids] or profiles
            profile, method = _auto_select_profile(available, topic, hints)

        if not profile:
            pool = [p for p in profiles if p.get("id") not in used_profile_ids] or profiles
            profile = pool[0] if pool else None
            method = "fallback"

        if profile:
            pid = profile.get("id", "")
            used_profile_ids.add(pid)
            voices[speaker] = {
                "voice_id":    profile.get("voice_id", ""),
                "name":        guest.get("name", f"Guest {i + 1}"),
                "profile_id":  pid,
                "selection_method": method,
            }
        else:
            voices[speaker] = {
                "voice_id": "",
                "name": guest.get("name", f"Guest {i + 1}"),
                "selection_method": "none",
            }

    return voices


EPISODE = load_episode()
EPISODE_AUDIO = EPISODE.get("audio", {}) if isinstance(EPISODE.get("audio"), dict) else {}
TARGET_PLAYBACK_SPEED = float(
    EPISODE_AUDIO.get("playback_speed")
    if EPISODE_AUDIO.get("playback_speed") is not None
    else PLAYBACK_SPEED_BY_LANGUAGE.get(SCRIPT_LANGUAGE, PLAYBACK_SPEED)
    if isinstance(PLAYBACK_SPEED_BY_LANGUAGE, dict)
    else PLAYBACK_SPEED
)
VOICES  = resolve_all_voices(EPISODE)

# Print voice resolution summary
if not SUPPRESS_INIT_OUTPUT:
    print(f"\nTTS Provider : EDGE_TTS (lang: {SCRIPT_LANGUAGE}, speed: {TARGET_PLAYBACK_SPEED:.2f}x)")
    for spk, info in VOICES.items():
        vid  = info.get("voice_id", "(missing)")
        name = info.get("name", "")
        how  = info.get("selection_method", "")
        prof = f"  [{info['profile_id']}]" if "profile_id" in info else ""
        print(f"  {spk:<10} → {vid:<16} ({name}){prof}  via {how}")

_missing_voices = [spk for spk, info in VOICES.items() if not info.get("voice_id")]
if _missing_voices and not SUPPRESS_INIT_OUTPUT:
    print(f"\nWARNING: missing voice_id for: {', '.join(_missing_voices)}")
    print("  → Set voice_id in voice_config.json for each speaker.")

AUDIO_ENABLED = not _missing_voices

# ── Script parser ─────────────────────────────────────────────────────────────

# Matches [HOST], [GUEST], [GUEST_1], [GUEST_2], [GUEST_3], ...
SPEAKER_RE  = re.compile(r"\[(HOST|GUEST(?:_\d+)?)\] (.+)")
TONE_CUE_RE  = re.compile(r"\[(cuoi[^\]]*|dung lai|nghiem tuc[^\]]*|nang dong[^\]]*|khe gat[^\]]*|laugh[^\]]*|pause|serious[^\]]*|energetic[^\]]*|reflective[^\]]*)\]", re.I)
BOLD_RE      = re.compile(r"\*{1,2}(.+?)\*{1,2}")
# Em-dash and standalone hyphens used as pauses (not in numbers like "COVID-19" or ranges "2020-2026")
DASH_PAUSE_RE = re.compile(r"\s*—\s*|\s+-\s+")
SEGMENT_PREFIX_RE = re.compile(r"^(segment|part|phần)\s*\d+\s*[:—-]\s*", re.I)
CLOSING_PREFIX_RE = re.compile(r"^closing\s*[:—-]\s*", re.I)

def sanitize_for_tts(text: str) -> str:
    """Strip tone cues, markdown bold, and dash-pauses that TTS reads aloud as 'gạch ngang'."""
    text = TONE_CUE_RE.sub("", text)
    text = BOLD_RE.sub(r"\1", text)
    text = DASH_PAUSE_RE.sub(", ", text)
    return text.strip()


def spoken_segment_title(label: str) -> str:
    """Turn a segment label into something natural for the host to say aloud."""
    title = label.strip()
    title = SEGMENT_PREFIX_RE.sub("", title)
    title = CLOSING_PREFIX_RE.sub("", title)
    title = re.sub(r"\s+", " ", title).strip(" .")
    return title


def is_closing_segment(label: str) -> bool:
    return bool(CLOSING_PREFIX_RE.match(label.strip()))


def maybe_add_segment_title_announcement(out: list[dict], idx: int, label: str) -> int:
    """Optionally insert a host-spoken section title after a segment break."""
    if not ANNOUNCE_SEGMENT_TITLES:
        return idx
    title = spoken_segment_title(label)
    if not title:
        return idx
    template = SEGMENT_CLOSING_TEMPLATE if is_closing_segment(label) else SEGMENT_TITLE_TEMPLATE
    text = sanitize_for_tts(template.format(title=title))
    if not text:
        return idx
    out.append({
        "type": "speech",
        "speaker": SEGMENT_TITLE_SPEAKER,
        "text": text,
        "idx": idx,
        "generated": "segment_title_announcement",
        "tts_profile": SEGMENT_TITLE_PROFILE,
        "pace_profile": SEGMENT_TITLE_CFG.get("pace_profile", ""),
    })
    return idx + 1


def parse_script(path: Path) -> list[dict]:
    """Return ordered list of segment dicts. [GUEST] is treated as [GUEST_1]."""
    out, idx = [], 0
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("|") or line.startswith("---"):
            continue

        if re.match(r"\[INTRO_MUSIC\]", line):
            out.append({"type": "music", "music_type": "intro", "label": "INTRO_MUSIC"})

        elif re.match(r"\[OUTRO_MUSIC\]", line):
            out.append({"type": "music", "music_type": "outro", "label": "OUTRO_MUSIC"})

        elif m := re.match(r"\[SEGMENT_BREAK:\s*(.+)\]", line):
            label = m.group(1).strip()
            out.append({"type": "sfx", "sfx_type": "segment_break", "label": label})
            idx = maybe_add_segment_title_announcement(out, idx, label)

        elif m := re.match(r"\[SOUND_EFFECT:\s*(.+)\]", line):
            out.append({"type": "sfx", "sfx_type": "custom", "label": m.group(1).strip()})

        elif m := SPEAKER_RE.match(line):
            raw_speaker = m.group(1)                          # HOST | GUEST | GUEST_2 …
            speaker     = "GUEST" if raw_speaker == "GUEST_1" else raw_speaker  # normalise _1
            text        = sanitize_for_tts(m.group(2))
            if text:
                out.append({"type": "speech", "speaker": speaker, "text": text, "idx": idx})
                idx += 1

    return out


# ── TTS: edge-tts ────────────────────────────────────────────────────────────

def tts_edge_tts(text: str, voice_id: str, out_path: Path) -> bool:
    """Free TTS using edge-tts CLI."""
    if not EDGE_TTS_BIN:
        print("    edge-tts not found in PATH")
        return False
    cmd = [EDGE_TTS_BIN, "--voice", voice_id, "--text", text, "--write-media", str(out_path)]
    for attempt in range(3):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=60)
            if result.returncode == 0 and out_path.exists() and out_path.stat().st_size > 0:
                return True
            if out_path.exists():
                out_path.unlink(missing_ok=True)
            err = result.stderr[:200] if result.stderr else "(no stderr)"
            print(f"    edge-tts attempt {attempt+1}/3 failed (rc={result.returncode}): {err}")
            if attempt < 2:
                time.sleep(2 ** attempt)
        except subprocess.TimeoutExpired:
            print(f"    edge-tts attempt {attempt+1}/3 timed out (60s) — retrying")
            if out_path.exists():
                out_path.unlink(missing_ok=True)
            if attempt < 2:
                time.sleep(2 ** attempt)
        except Exception as e:
            print(f"    edge-tts error: {e}")
            return False
    return False


def tts(text: str, voice_id: str, out_path: Path, **_kw) -> tuple[bool, list[dict]]:
    """Generate TTS audio via edge-tts."""
    t0 = time.time()
    ok = tts_edge_tts(text, voice_id, out_path)
    return ok, [{"ok": ok, "elapsed_s": round(time.time() - t0, 3)}]


def _atempo_chain(speed: float) -> list[str]:
    if speed <= 0 or abs(speed - 1.0) <= 1e-3:
        return []
    filters: list[str] = []
    s = speed
    while s > 2.0:
        filters.append("atempo=2.0")
        s /= 2.0
    while s < 0.5:
        filters.append("atempo=0.5")
        s *= 2.0
    filters.append(f"atempo={s:.3f}")
    return filters


def apply_playback_speed_to_speech(path: Path, speed: float) -> bool:
    """Apply speed change to one speech segment only, preserving pitch."""
    if not path.exists() or speed <= 0 or abs(speed - 1.0) <= 1e-3:
        return True
    if not FFMPEG_BIN:
        return False

    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        temp_out = Path(f.name)
    try:
        af = ",".join(_atempo_chain(speed))
        cmd = [
            FFMPEG_BIN, "-y",
            "-i", str(path),
            "-af", af,
            "-codec:a", "libmp3lame",
            "-b:a", OUTPUT_BITRATE,
            str(temp_out),
        ]
        run = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if run.returncode != 0:
            print(f"    ⚠ speech speed transform failed: {run.stderr[:200]}")
            return False
        temp_out.replace(path)
        return True
    finally:
        if temp_out.exists():
            try:
                temp_out.unlink()
            except Exception:
                pass


# ── Fixed asset preparation ───────────────────────────────────────────────────

def resolve_music_assets(segments: list[dict]) -> dict[str, Path]:
    music_map: dict[str, Path] = {}
    for mtype in {s["music_type"] for s in segments if s["type"] == "music"}:
        if ASSETS_DIR:
            src = ASSETS_DIR / f"{mtype}.mp3"
            if src.exists():
                music_map[mtype] = src
                print(f"  [MUSIC:{mtype}] shared asset ✓")
                continue
        print(f"  [MUSIC:{mtype}] ⚠ shared asset not found — silence gap will be used")
    return music_map


def resolve_sfx_assets(segments: list[dict]) -> None:
    sfx_segs = [s for s in segments if s["type"] == "sfx"]
    if not sfx_segs:
        return
    out_path = ASSETS_DIR / "transition.mp3" if ASSETS_DIR else None
    if out_path and out_path.exists():
        print("  [SFX] shared transition asset ✓")
    else:
        print("  [SFX] ⚠ shared transition asset not found")
    for seg in sfx_segs:
        label = seg.get("label", "sfx")[:50]
        if out_path and out_path.exists():
            seg["_sfx_path"] = out_path
            print(f"  [SFX] {label} → transition ✓")
        else:
            print(f"  [SFX] {label} → ⚠ skipped (no asset)")


# ── Speech generation ─────────────────────────────────────────────────────────

def prepare_speech(segments: list[dict]) -> dict[int, Path]:
    """Generate TTS audio for all speech segments in parallel."""
    speech_segs = [s for s in segments if s["type"] == "speech"]
    audio_map: dict[int, Path] = {}

    print(f"\n  Generating TTS ({TTS_PROVIDER}) for {len(speech_segs)} speech segments…\n")
    speed_tag = f"s{int(round(TARGET_PLAYBACK_SPEED * 100)):03d}"
    provider_tag = TTS_PROVIDER.replace("-", "_")

    def _process_seg(i: int, seg: dict) -> tuple[int, bool, Path]:
        speaker  = seg["speaker"]
        info     = VOICES.get(speaker) or VOICES.get("GUEST", {})
        voice_id = info.get("voice_id", "")
        label    = f"{speaker} ({info.get('name', '')})"
        profile_label = info.get("profile_id", "")
        out_path = SEGS_DIR / f"seg_{seg['idx']:04d}_{speaker}_{provider_tag}_{speed_tag}.mp3"

        # Content-hash cache: derive a stable path from (text, voice_id, profile, speed)
        # so segments survive episode re-runs when text is unchanged regardless of idx shift.
        _cache_src = f"{seg.get('text','')}\x00{voice_id}\x00{profile_label}\x00{TARGET_PLAYBACK_SPEED}"
        _content_hash = hashlib.md5(_cache_src.encode()).hexdigest()[:10]
        hash_path = SEGS_DIR / f"seg_{seg['idx']:04d}_{speaker}_{provider_tag}_{speed_tag}_{_content_hash}.mp3"

        # 1) Check content-hash path first (canonical cache file)
        if hash_path.exists() and hash_path.stat().st_size > 2048:
            if out_path.is_symlink() or not out_path.exists():
                out_path.unlink(missing_ok=True)
                out_path.symlink_to(hash_path.name)
            print(f"  [{i+1:>3}/{len(speech_segs)}] {label} — cached ✓")
            _record_benchmark({
                "idx": seg["idx"],
                "speaker": speaker,
                "chars": len(seg.get("text", "")),
                "cached": True,
                "ok": True,
                "attempts": [],
                "output": str(out_path),
            })
            return seg["idx"], True, out_path

        # 2) Check index-based path (backward compat with pre-symlink cache)
        if out_path.exists() and not out_path.is_symlink() and out_path.stat().st_size > 2048:
            print(f"  [{i+1:>3}/{len(speech_segs)}] {label} — cached ✓")
            _record_benchmark({
                "idx": seg["idx"],
                "speaker": speaker,
                "chars": len(seg.get("text", "")),
                "cached": True,
                "ok": True,
                "attempts": [],
                "output": str(out_path),
            })
            return seg["idx"], True, out_path

        if SCRIPT_LANGUAGE == "vi":
            # Convert written-tech phrasing into more speakable Vietnamese before phonetic normalization.
            text = polish_text(seg["text"], EPISODE.get("topic", ""))
            text = normalize_text(text)
        else:
            text = seg["text"]
        ok, attempts = tts(text, voice_id, out_path)
        if ok and TARGET_PLAYBACK_SPEED > 0 and abs(TARGET_PLAYBACK_SPEED - 1.0) > 1e-3:
            ok = apply_playback_speed_to_speech(out_path, TARGET_PLAYBACK_SPEED)
        # Move the rendered file to the content-hash path (canonical) and
        # symlink the index-based path to it.  This avoids storing two
        # identical copies of every segment on disk.
        if ok and out_path.exists() and not out_path.is_symlink() and out_path.stat().st_size > 2048:
            try:
                shutil.move(str(out_path), str(hash_path))
                out_path.symlink_to(hash_path.name)
            except Exception:
                pass
        _record_benchmark({
            "idx": seg["idx"],
            "speaker": speaker,
            "chars": len(seg.get("text", "")),
            "cached": False,
            "ok": ok,
            "attempts": attempts,
            "output": str(out_path),
        })
        return seg["idx"], ok, out_path

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(_process_seg, i, seg): (i, seg) for i, seg in enumerate(speech_segs)}
        for future in as_completed(futures):
            idx, ok, out_path = future.result()
            if ok:
                audio_map[idx] = out_path
            else:
                print(f"    ⚠ TTS failed for segment index {idx} — silence gap inserted")

    return audio_map


# ── Merge ─────────────────────────────────────────────────────────────────────

def load_audio(path: Path) -> AudioSegment | None:
    try:
        return AudioSegment.from_mp3(str(path))
    except Exception as e:
        print(f"    ⚠ could not load {path.name}: {e}")
        return None


def sentence_count(text: str) -> int:
    count = len(re.findall(r"[.!?…]+", text))
    return count or 1


def is_short_reaction(seg: dict) -> bool:
    if seg.get("type") != "speech":
        return False
    text = seg.get("text", "").strip()
    max_chars = PAUSE_RULES.get("short_reaction_max_chars", 95)
    max_sentences = PAUSE_RULES.get("short_reaction_max_sentences", 1)
    return len(text) <= max_chars and sentence_count(text) <= max_sentences


def gap_after(seg: dict, next_seg: dict | None) -> int:
    if not next_seg:
        return 0

    stype = seg["type"]
    if stype == "music":
        return PAUSE_RULES.get("after_music_ms", GAP_MUSIC)
    if stype == "sfx":
        if next_seg.get("generated") == "segment_title_announcement":
            return PAUSE_RULES.get("after_sfx_before_announcement_ms", 120)
        return PAUSE_RULES.get("after_segment_break_ms", GAP_SEGMENT)
    if stype != "speech":
        return 0

    if next_seg["type"] != "speech":
        return PAUSE_RULES.get("before_non_speech_ms", 0)
    if seg.get("generated") == "segment_title_announcement" or next_seg.get("generated") == "segment_title_announcement":
        return PAUSE_RULES.get("after_generated_announcement_ms", 220)
    if seg["speaker"] == next_seg["speaker"]:
        return PAUSE_RULES.get("same_speaker_ms", 220)
    if is_short_reaction(seg) or is_short_reaction(next_seg):
        return PAUSE_RULES.get("short_reaction_ms", 180)
    if seg["speaker"] == "HOST" and next_seg["speaker"].startswith("GUEST"):
        return PAUSE_RULES.get("host_to_guest_ms", GAP_TURN)
    if seg["speaker"].startswith("GUEST") and next_seg["speaker"] == "HOST":
        return PAUSE_RULES.get("guest_to_host_ms", GAP_TURN)
    return PAUSE_RULES.get("default_turn_ms", GAP_TURN)


def export_mp3_with_loudness(result: AudioSegment, out_path: Path, tags: dict[str, str]) -> None:
    import tempfile

    working = result.set_frame_rate(AUDIO_CFG.get("sample_rate_hz", 44100)).set_channels(AUDIO_CFG.get("channels", 2))
    metadata_args: list[str] = []
    for key, value in tags.items():
        metadata_args.extend(["-metadata", f"{key}={value}"])

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_in:
        working.export(temp_in.name, format="wav")
        temp_in_path = temp_in.name

    try:
        loudnorm_enabled = LOUDNESS_CFG.get("enabled", True)
        if loudnorm_enabled and FFMPEG_BIN:
            filter_str = (
                "loudnorm="
                f"I={LOUDNESS_CFG.get('integrated_lufs', -16)}:"
                f"TP={LOUDNESS_CFG.get('true_peak_dbtp', -1.5)}:"
                f"LRA={LOUDNESS_CFG.get('lra', 8)}"
            )
            cmd = [
                FFMPEG_BIN, "-y", "-i", temp_in_path,
                "-af", filter_str,
                "-codec:a", "libmp3lame",
                "-b:a", OUTPUT_BITRATE,
                *metadata_args,
                str(out_path),
            ]
            result_ffmpeg = subprocess.run(cmd, capture_output=True, text=True)
            if result_ffmpeg.returncode == 0:
                return
            print(f"    ⚠ loudnorm export failed, falling back to plain MP3: {result_ffmpeg.stderr[:200]}")

        working.export(str(out_path), format="mp3", bitrate=OUTPUT_BITRATE, tags=tags)
    finally:
        os.unlink(temp_in_path)


def ffprobe_audio(path: Path) -> dict:
    if not FFPROBE_BIN or not path.exists():
        return {}
    cmd = [
        FFPROBE_BIN,
        "-v", "error",
        "-show_entries", "format=duration,bit_rate:stream=codec_name,bit_rate,sample_rate,channels",
        "-of", "json",
        str(path),
    ]
    try:
        data = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(data.stdout)
    except Exception:
        return {}


def loudness_stats(path: Path) -> dict:
    if not FFMPEG_BIN or not path.exists():
        return {}
    filter_str = (
        "loudnorm="
        f"I={LOUDNESS_CFG.get('integrated_lufs', -16)}:"
        f"TP={LOUDNESS_CFG.get('true_peak_dbtp', -1.5)}:"
        f"LRA={LOUDNESS_CFG.get('lra', 8)}:print_format=summary"
    )
    cmd = [FFMPEG_BIN, "-i", str(path), "-af", filter_str, "-f", "null", "-"]
    try:
        stderr = subprocess.run(cmd, capture_output=True, text=True, check=False).stderr
        stats = {}
        for key, pattern in {
            "input_integrated_lufs": r"Input Integrated:\s+(-?[0-9.]+) LUFS",
            "input_true_peak_dbtp": r"Input True Peak:\s+(-?[0-9.]+) dBTP",
            "input_lra": r"Input LRA:\s+([0-9.]+) LU",
            "output_integrated_lufs": r"Output Integrated:\s+(-?[0-9.]+) LUFS",
            "output_true_peak_dbtp": r"Output True Peak:\s+(-?[0-9.]+) dBTP",
            "output_lra": r"Output LRA:\s+([0-9.]+) LU",
        }.items():
            match = re.search(pattern, stderr)
            if match:
                stats[key] = float(match.group(1))
        return stats
    except Exception:
        return {}


def silence_stats(path: Path) -> dict:
    if not FFMPEG_BIN or not path.exists():
        return {}
    cmd = [FFMPEG_BIN, "-i", str(path), "-af", "silencedetect=noise=-35dB:d=0.35", "-f", "null", "-"]
    try:
        stderr = subprocess.run(cmd, capture_output=True, text=True, check=False).stderr
        durations = [float(m.group(1)) for m in re.finditer(r"silence_duration: ([0-9.]+)", stderr)]
        if not durations:
            return {"count": 0, "sum_seconds": 0, "avg_seconds": 0, "max_seconds": 0}
        return {
            "count": len(durations),
            "sum_seconds": round(sum(durations), 3),
            "avg_seconds": round(sum(durations) / len(durations), 3),
            "max_seconds": round(max(durations), 3),
        }
    except Exception:
        return {}


def risk_term_report(script_path: Path) -> dict:
    terms = POLISH_CFG.get("risk_terms", [])
    if not script_path.exists() or not isinstance(terms, list):
        return {}
    spoken_lines = [
        line for line in script_path.read_text().splitlines()
        if re.match(r"^\[(?:HOST|GUEST(?:_\d+)?)\]", line)
    ]
    joined = "\n".join(spoken_lines)
    report = {}
    for term in terms:
        matches = re.findall(re.escape(term), joined, flags=re.IGNORECASE)
        if matches:
            report[term] = len(matches)
    return report


def write_qa_report(out_path: Path, script_path: Path, speaker_counts: dict[str, int]) -> None:
    report = {
        "output": str(out_path),
        "audio_probe": ffprobe_audio(out_path),
        "loudness": loudness_stats(out_path),
        "silence": silence_stats(out_path),
        "risk_terms": risk_term_report(script_path),
        "speaker_counts": speaker_counts,
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    report_path = BASE / "qa_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"  qa_report.json written")


def write_benchmark_report(out_path: Path) -> None:
    if not RUN_BENCHMARK:
        return

    with BENCH_LOCK:
        records = list(BENCHMARK_RECORDS)

    active = [r for r in records if not r.get("cached")]
    attempt_count = sum(len(r.get("attempts", [])) for r in active)
    tts_runtime = round(
        sum(a.get("elapsed_s", 0.0) for r in active for a in r.get("attempts", [])),
        3,
    )

    audio_duration_seconds = 0.0
    for rec in active:
        p = Path(rec.get("output", ""))
        if not p.exists():
            continue
        try:
            audio_duration_seconds += len(AudioSegment.from_mp3(str(p))) / 1000.0
        except Exception:
            pass
    audio_duration_seconds = round(audio_duration_seconds, 3)
    rtf = round(tts_runtime / audio_duration_seconds, 4) if audio_duration_seconds > 0 else None

    summary = {
        "enabled": True,
        "provider": TTS_PROVIDER,
        "engine_mode_requested": "",
        "segments_total": len(records),
        "segments_generated": len(active),
        "attempt_count": attempt_count,
        "tts_runtime_seconds": tts_runtime,
        "audio_duration_seconds_generated": audio_duration_seconds,
        "rtf": rtf,
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "output": str(out_path),
        "records": records,
    }
    benchmark_path = BASE / "benchmark_report.json"
    benchmark_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print("  benchmark_report.json written")


def write_workspace_manifest(
    script_path: Path,
    final_mp3: Path,
    music_map: dict[str, Path],
    speaker_counts: dict[str, int],
    speech_total: int,
    speech_generated: int,
    sfx_total: int,
) -> None:
    request_data = _read_json(BASE / "request.json")
    manifest = {
        "workspace": str(BASE),
        "episode": BASE.name,
        "request": str(BASE / "request.json") if (BASE / "request.json").exists() else "",
        "episode_config": str(BASE / "episode.json"),
        "scripts": {
            "selected": str(script_path),
            "english": str(BASE / "script_en.txt") if (BASE / "script_en.txt").exists() else "",
            "vietnamese": str(BASE / "script_vi.txt") if (BASE / "script_vi.txt").exists() else "",
        },
        "research": {
            "merged": str(BASE / "research.json") if (BASE / "research.json").exists() else "",
            "dir": str(BASE / "research") if (BASE / "research").exists() else "",
        },
        "prompts_dir": str(BASE / "prompts") if (BASE / "prompts").exists() else "",
        "logs_dir": str(LOGS_DIR),
        "cache": {
            "segments_dir": str(SEGS_DIR),
        },
        "shared_resources": {
            "produce_audio_script": str(Path(__file__).resolve()),
            "voice_config": str((ASSETS_DIR / "voice_config.json").resolve()) if ASSETS_DIR else "",
            "assets_dir": str(ASSETS_DIR.resolve()) if ASSETS_DIR else "",
            "music_assets": {key: str(path) for key, path in music_map.items()},
            "transition_asset": str((ASSETS_DIR / "transition.mp3").resolve()) if ASSETS_DIR and (ASSETS_DIR / "transition.mp3").exists() else "",
        },
        "render": {
            "tts_provider": TTS_PROVIDER,
            "speech_total": speech_total,
            "speech_generated": speech_generated,
            "speaker_counts": speaker_counts,
            "sfx_total": sfx_total,
            "output": str(final_mp3),
        },
        "request_summary": request_data,
        "updated_at": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    _write_json(WORKSPACE_MANIFEST_PATH, manifest)


def merge(segments: list[dict], audio_map: dict[int, Path], music_map: dict[str, Path],
          out_path: Path, episode_title: str = "") -> None:
    result = AudioSegment.empty()
    sil_cache: dict[int, AudioSegment] = {}

    def sil(ms: int) -> AudioSegment:
        if ms not in sil_cache:
            sil_cache[ms] = AudioSegment.silent(duration=ms)
        return sil_cache[ms]

    for idx, seg in enumerate(segments):
        next_seg = segments[idx + 1] if idx + 1 < len(segments) else None
        stype = seg["type"]
        if stype == "music":
            p = music_map.get(seg["music_type"])
            if p and p.exists():
                audio = load_audio(p)
                if audio:
                    result += audio
        elif stype == "sfx":
            sfx_path = seg.get("_sfx_path")
            if sfx_path and sfx_path.exists():
                audio = load_audio(sfx_path)
                if audio:
                    result += audio
        elif stype == "speech":
            p = audio_map.get(seg["idx"])
            if p and p.exists():
                audio = load_audio(p)
                if audio:
                    result += audio
        pause_ms = gap_after(seg, next_seg)
        if pause_ms > 0:
            result += sil(pause_ms)

    tags = {
        "title":  episode_title or BASE.name,
        "artist": "Tech Radar Podcast",
        "album":  "Tech Radar",
        "genre":  "Technology",
        "date":   datetime.date.today().isoformat(),
    }
    export_mp3_with_loudness(result, out_path, tags)
    mins = len(result) / 60000
    print(f"\n  {out_path.name}  |  {mins:.1f} min  |  {out_path.stat().st_size / 1024:.0f} KB")


# ── Main ──────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tech Radar podcast audio production")
    parser.add_argument(
        "--workspace",
        default=str(BASE),
        help="Episode workspace directory under podcast_studio/",
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Record per-segment TTS latency and write benchmark_report.json",
    )
    return parser.parse_args()


def main() -> None:
    update_status("audio_render", "running", {"workspace": str(BASE)})
    script_path = resolve_script_path(BASE, SCRIPT_LANGUAGE)
    final_mp3   = EXPORTS_DIR / f"{BASE.name}_{SCRIPT_LANGUAGE}_final.mp3"

    print(f"\nTech Radar — Audio Production v7 (edge-tts)")
    print(f"  Workspace: {BASE}")
    print(f"  Script   : {script_path}")
    print(f"  Output   : {final_mp3}")
    print(f"  Provider : {TTS_PROVIDER.upper()}")
    if RUN_BENCHMARK:
        print("  Benchmark: ON")
    print(f"  Assets   : {ASSETS_DIR or 'NOT FOUND — fixed audio will be skipped'}\n")

    segments = parse_script(script_path)
    episode_meta = load_episode()
    enforce_duration_guardrails(segments, episode_meta, SCRIPT_LANGUAGE)
    speech_count = sum(1 for s in segments if s["type"] == "speech")
    music_count  = sum(1 for s in segments if s["type"] == "music")
    sfx_count    = sum(1 for s in segments if s["type"] == "sfx")

    # Count per-speaker breakdown
    speaker_counts: dict[str, int] = {}
    for s in segments:
        if s["type"] == "speech":
            speaker_counts[s["speaker"]] = speaker_counts.get(s["speaker"], 0) + 1
    breakdown = "  ".join(f"{spk}={n}" for spk, n in sorted(speaker_counts.items()))
    print(f"  Parsed: {speech_count} speech ({breakdown}) | {music_count} music | {sfx_count} SFX\n")

    if not AUDIO_ENABLED:
        print("Audio generation skipped (missing config/env vars).")
        update_status("audio_render", "blocked", {"reason": "missing audio config"})
        return

    print("PHASE A — Music assets")
    music_map = resolve_music_assets(segments)

    print("\nPHASE B — Transition asset")
    resolve_sfx_assets(segments)

    print("\nPHASE C — TTS speech generation (edge-tts)")
    audio_map = prepare_speech(segments)

    generated = len(audio_map)
    print(f"\nPHASE D — Merging {generated}/{speech_count} speech + {len(music_map)} music + {sfx_count} SFX…")

    episode_title = ""
    for line in script_path.read_text().splitlines():
        if line.startswith("# "):
            episode_title = line[2:].strip()
            break

    merge(segments, audio_map, music_map, final_mp3, episode_title)

    # Smart manifest
    manifest = {
        "episode":   BASE.name,
        "title":     episode_title,
        "tts_provider": TTS_PROVIDER,
        "voices":    VOICES,
        "segments": {
            "speech": {"total": speech_count, "generated": generated, "by_speaker": speaker_counts},
            "music":  music_count,
            "sfx":    sfx_count,
        },
        "output": str(final_mp3),
        "date":   datetime.date.today().isoformat(),
        "workspace": str(BASE),
        "cache_segments_dir": str(SEGS_DIR),
    }
    (BASE / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"  manifest.json written\n")
    write_workspace_manifest(script_path, final_mp3, music_map, speaker_counts, speech_count, generated, sfx_count)
    write_qa_report(final_mp3, script_path, speaker_counts)
    write_benchmark_report(final_mp3)
    update_status("audio_render", "completed", {"output": str(final_mp3), "speech_generated": generated})

    print(f"  ✓ Final audio: {final_mp3}")


if __name__ == "__main__":
    args = parse_args()
    if args.benchmark:
        RUN_BENCHMARK = True
    main()
