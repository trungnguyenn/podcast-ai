#!/usr/bin/env python3
"""Tech Radar — Audio Production v6
Pipeline: parse script → shared fixed assets → TTS → merge MP3
Supports TTS providers: vieneu (local), elevenlabs (cloud), edge-tts (free), macos-say (free).
Supports multiple guests: [GUEST] or [GUEST_1], [GUEST_2], ... in script.
Select provider via TTS_PROVIDER env var or tts_provider in voice_config.json.
Provider `auto` routes EN scripts to free community TTS (edge-tts, fallback say) and VI scripts to VieNeu.
"""

import os, re, json, time, shutil, datetime, requests, subprocess, sys, argparse, threading, hashlib
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
        ".agents/skills/tech-radar-podcast/assets/voice_config.json"
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
        ".agents/skills/tech-radar-podcast/assets"
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
VIENEU_CFG = CONFIG.get("vieneu", {})
VIENEU_DEFAULT_REQUEST = VIENEU_CFG.get("default_request", {})
VIENEU_VOICE_PROFILES = VIENEU_CFG.get("profiles", {})
VIENEU_PACE_PROFILES = VIENEU_CFG.get("pace_profiles", {})
VIENEU_ENGINE_CFG = VIENEU_CFG.get("engine", {})
VIENEU_FALLBACK_CFG = VIENEU_CFG.get("fallback_standard_to_turbo", {})
VIENEU_TURBO_RETRY_REQUEST = VIENEU_CFG.get("turbo_retry_request", {})
VIENEU_INTER_SEG_SLEEP = float(VIENEU_CFG.get("inter_segment_sleep_s", 0.0))
POLISH_CFG = CONFIG.get("tts_polish", {})
ASSETS_DIR = find_assets_dir()
SEGMENT_TITLE_CFG = AUDIO_CFG.get("segment_title_announcement", {})
LOUDNESS_CFG = AUDIO_CFG.get("loudness_normalization", {})
PAUSE_RULES = AUDIO_CFG.get("pause_rules", {})
OUTPUT_BITRATE = AUDIO_CFG.get("bitrate", "128k")
PLAYBACK_SPEED = float(AUDIO_CFG.get("playback_speed", 1.0))
PLAYBACK_SPEED_BY_LANGUAGE = AUDIO_CFG.get("playback_speed_by_language", {})
COMMUNITY_CFG = CONFIG.get("community_tts", {})
RUN_BENCHMARK = os.environ.get("PODCAST_BENCHMARK", "").strip().lower() in {"1", "true", "yes"}
BENCHMARK_RECORDS: list[dict] = []
BENCH_LOCK = threading.Lock()

_SERVER_ENGINE_MODE = ""
_SERVER_ENGINE_LOCK = threading.Lock()

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
SAY_BIN = _find_binary("say")


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
        # Case insensitive for lowercase keys in config
        flags = re.IGNORECASE if key[0].islower() else 0
        fixed = re.sub(pattern, val, fixed, flags=flags)
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


# ── TTS provider selection ────────────────────────────────────────────────────

REQUESTED_TTS_PROVIDER = (os.environ.get("TTS_PROVIDER") or CONFIG.get("tts_provider", "vieneu")).lower()
SCRIPT_LANGUAGE = (
    (os.environ.get("PODCAST_LANG") or "").strip().lower()
    or detect_episode_language(BASE / "episode.json")
)
if SCRIPT_LANGUAGE not in {"vi", "en"}:
    SCRIPT_LANGUAGE = "vi"


def resolve_script_path(base: Path, lang: str) -> Path:
    """Pick the right script file based on language, with fallbacks."""
    # Prefer language-specific .txt files
    lang_file = base / f"script_{lang}.txt"
    if lang_file.exists():
        return lang_file
    # Fallback: try the other language
    other = "en" if lang == "vi" else "vi"
    other_file = base / f"script_{other}.txt"
    if other_file.exists():
        return other_file
    # Legacy fallback: script.md
    legacy = base / "script.md"
    if legacy.exists():
        return legacy
    # Default (will fail with a clear error at parse time)
    return lang_file

VIENEU_URL  = os.environ.get("VIENEU_URL") or VIENEU_CFG.get("url", "http://127.0.0.1:8001")

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
EL_CFG      = CONFIG.get("elevenlabs", {})
EL_MODEL    = EL_CFG.get("model", "eleven_multilingual_v2")
EL_API_URL  = EL_CFG.get("api_url", "https://api.elevenlabs.io")
EL_SETTINGS = EL_CFG.get("voice_settings", {
    "stability": 0.50, "similarity_boost": 0.75,
    "style": 0.35, "use_speaker_boost": True,
})

def _pick_auto_provider() -> str:
    if SCRIPT_LANGUAGE == "en":
        if EDGE_TTS_BIN:
            return "edge_tts"
        if SAY_BIN:
            return "macos_say"
        return "vieneu"
    return "vieneu"

if REQUESTED_TTS_PROVIDER == "auto":
    TTS_PROVIDER = _pick_auto_provider()
else:
    TTS_PROVIDER = REQUESTED_TTS_PROVIDER


def _normalize_engine_mode(mode: str) -> str:
    m = (mode or "").strip().lower()
    if m in {"standard", "turbo", "turbo_gpu", "auto"}:
        return m
    return "standard"


def _extract_clone_fields(data: dict) -> dict:
    clone = data.get("voice_clone", {}) if isinstance(data, dict) else {}
    if not isinstance(clone, dict):
        clone = {}
    return {
        "ref_audio": data.get("ref_audio", clone.get("ref_audio", "")),
        "ref_text": data.get("ref_text", clone.get("ref_text", "")),
        "ref_codes": data.get("ref_codes", clone.get("ref_codes")),
    }


def _episode_render_intent(ep: dict) -> set[str]:
    intent_tokens: set[str] = set()
    for key in ("render_purpose", "purpose", "mode", "stage", "intent"):
        val = ep.get(key)
        if not val:
            continue
        parts = re.split(r"[,/|_\s-]+", str(val).lower())
        intent_tokens.update(p for p in parts if p)
    return intent_tokens


def resolve_vieneu_engine_mode(ep: dict) -> str:
    requested = _normalize_engine_mode(
        os.environ.get("VIENEU_ENGINE_MODE")
        or VIENEU_ENGINE_CFG.get("mode", "standard")
    )
    if requested != "auto":
        return requested

    intents = _episode_render_intent(ep)
    if intents & {"draft", "preview", "scratch", "fast"}:
        auto_mode = _normalize_engine_mode(VIENEU_ENGINE_CFG.get("auto_draft_mode", "turbo"))
        return "turbo" if auto_mode == "auto" else auto_mode
    return _normalize_engine_mode(VIENEU_ENGINE_CFG.get("auto_final_mode", "standard"))

TARGET_PLAYBACK_SPEED = float(
    PLAYBACK_SPEED_BY_LANGUAGE.get(SCRIPT_LANGUAGE, PLAYBACK_SPEED)
    if isinstance(PLAYBACK_SPEED_BY_LANGUAGE, dict)
    else PLAYBACK_SPEED
)

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

PROVIDER_VOICE_KEY = {
    "vieneu": "vieneu_voice_id",
    "elevenlabs": "elevenlabs_voice_id",
    "edge_tts": "edge_tts_voice_id",
    "macos_say": "say_voice_id",
}
VKEY = PROVIDER_VOICE_KEY.get(TTS_PROVIDER, "vieneu_voice_id")


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


def _resolve_vieneu_profile_request(profile_name: str | None) -> dict:
    if not profile_name:
        return {}
    profile = VIENEU_VOICE_PROFILES.get(profile_name)
    if isinstance(profile, dict):
        return dict(profile)
    print(f"    WARNING: VieNeu profile '{profile_name}' not found in config")
    return {}


def _resolve_vieneu_pace_request(profile_name: str | None) -> dict:
    if not profile_name:
        return {}
    profile = VIENEU_PACE_PROFILES.get(profile_name)
    if isinstance(profile, dict):
        return dict(profile)
    print(f"    WARNING: VieNeu pace profile '{profile_name}' not found in config")
    return {}


def _merge_request_layers(*layers: dict | None) -> dict:
    merged: dict = {}
    for layer in layers:
        if not isinstance(layer, dict):
            continue
        for key, value in layer.items():
            if value is None or value == "":
                continue
            merged[key] = value
    return merged


def _voice_request_from_config(cfg: dict) -> dict:
    merged: dict = {}
    for layer in (
        _resolve_vieneu_profile_request(cfg.get("vieneu_profile", "")),
        _resolve_vieneu_pace_request(cfg.get("pace_profile", "")),
        cfg.get("vieneu_request", {}),
    ):
        if not isinstance(layer, dict):
            continue
        for key, value in layer.items():
            if value is None or value == "":
                continue
            merged[key] = value
    return merged


def _record_benchmark(record: dict) -> None:
    if not RUN_BENCHMARK:
        return
    with BENCH_LOCK:
        BENCHMARK_RECORDS.append(record)


def _default_voice_for_provider(provider: str, speaker: str, gender: str = "", profile_id: str = "") -> str:
    """Return a sensible free-English fallback voice when provider-specific IDs are missing."""
    provider_defaults = COMMUNITY_CFG.get("defaults", {}) if isinstance(COMMUNITY_CFG, dict) else {}
    if provider == "edge_tts":
        edge_cfg = provider_defaults.get("edge_tts", {})
        if speaker == "HOST":
            return edge_cfg.get("host") or "en-US-AndrewMultilingualNeural"
        if (gender or "").lower().startswith("f"):
            return edge_cfg.get("female_guest") or "en-US-AvaMultilingualNeural"
        if (gender or "").lower().startswith("m"):
            return edge_cfg.get("male_guest") or "en-US-BrianMultilingualNeural"
        if "female" in profile_id:
            return edge_cfg.get("female_guest") or "en-US-AvaMultilingualNeural"
        return edge_cfg.get("male_guest") or "en-US-BrianMultilingualNeural"

    if provider == "macos_say":
        say_cfg = provider_defaults.get("macos_say", {})
        if speaker == "HOST":
            return say_cfg.get("host") or "Samantha"
        if (gender or "").lower().startswith("f") or "female" in profile_id:
            return say_cfg.get("female_guest") or "Samantha"
        return say_cfg.get("male_guest") or "Alex"

    return ""


def resolve_all_voices(ep: dict) -> dict[str, dict]:
    """
    Returns {SPEAKER: voice_info} for HOST and all GUESTs.
    Speaker keys: HOST, GUEST (=first guest), GUEST_2, GUEST_3, ...
    Each voice_info: {voice_id, name, role?, profile_id?, profile_description?, selection_method}
    """
    guests     = episode_guests(ep)
    topic      = ep.get("topic", "")
    profiles   = CONFIG.get("guest_voices", [])
    voices: dict[str, dict] = {}

    # ── HOST ──
    host_cfg = CONFIG.get("host", {})
    host_clone = _extract_clone_fields(host_cfg)
    host_voice = os.environ.get("HOST_VOICE_ID") or host_cfg.get(VKEY, "")
    if not host_voice and TTS_PROVIDER in {"edge_tts", "macos_say"}:
        host_voice = _default_voice_for_provider(TTS_PROVIDER, "HOST", host_cfg.get("gender", ""))
    voices["HOST"] = {
        "voice_id":         host_voice,
        "name":             host_cfg.get("name", "Trung"),
        "profile":          "host",
        "region":           host_cfg.get("region", ""),
        "pace":             host_cfg.get("pace", ""),
        "energy":           host_cfg.get("energy", ""),
        "vieneu_profile":   host_cfg.get("vieneu_profile", ""),
        "pace_profile":     host_cfg.get("pace_profile", ""),
        "vieneu_request":   _voice_request_from_config(host_cfg),
        "ref_audio":        host_clone["ref_audio"],
        "ref_text":         host_clone["ref_text"],
        "ref_codes":        host_clone["ref_codes"],
        "selection_method": "config",
    }

    # ── GUESTs ──
    used_profile_ids: set[str] = set()

    for i, guest in enumerate(guests):
        guest_clone = _extract_clone_fields(guest)
        # Speaker key: GUEST for first, GUEST_2 / GUEST_3 ... for subsequent
        speaker    = "GUEST" if i == 0 else f"GUEST_{i + 1}"
        env_vid    = f"GUEST_VOICE_ID"    if i == 0 else f"GUEST_{i+1}_VOICE_ID"
        env_prof   = f"GUEST_VOICE_PROFILE" if i == 0 else f"GUEST_{i+1}_VOICE_PROFILE"

        # 1. Explicit voice ID override
        override_id = os.environ.get(env_vid, "")
        if override_id:
            explicit_profile = os.environ.get(env_prof, "") or guest.get("voice_profile", "")
            voices[speaker] = {
                "voice_id":         override_id,
                "name":             guest.get("name", f"Guest {i + 1}"),
                "role":             guest.get("role", ""),
                "region":           guest.get("region", ""),
                "pace":             guest.get("pace", ""),
                "energy":           guest.get("energy", ""),
                "vieneu_profile":   explicit_profile,
                "pace_profile":     guest.get("pace_profile", ""),
                "vieneu_request":   _merge_request_layers(
                    _resolve_vieneu_profile_request(explicit_profile),
                    _resolve_vieneu_pace_request(guest.get("pace_profile", "")),
                    guest.get("vieneu_request", {}),
                ),
                "ref_audio":        guest_clone["ref_audio"],
                "ref_text":         guest_clone["ref_text"],
                "ref_codes":        guest_clone["ref_codes"],
                "selection_method": f"env:{env_vid}",
            }
            continue

        # 2. Profile selection: explicit > topic auto-select > first unused > first overall
        profile: dict | None = None
        method = ""
        hints = _speaker_hint_values(ep, guest)

        explicit_profile = os.environ.get(env_prof, "") or guest.get("voice_profile", "")
        if explicit_profile:
            profile = next((p for p in profiles if p.get("id") == explicit_profile), None)
            if profile:
                method = f"explicit:{explicit_profile}"
            else:
                print(f"    WARNING: voice_profile '{explicit_profile}' not found in config")

        if not profile and topic:
            available = [p for p in profiles if p.get("id") not in used_profile_ids] or profiles
            profile, method = _auto_select_profile(available, topic, hints)
            if profile:
                pass

        if not profile:
            fallback_pool = [p for p in profiles if p.get("id") not in used_profile_ids] or profiles
            profile = fallback_pool[0] if fallback_pool else None
            method = "fallback (first available)"

        if profile:
            pid = profile.get("id", "")
            profile_clone = _extract_clone_fields(profile)
            used_profile_ids.add(pid)
            resolved_voice_id = profile.get(VKEY, "")
            if not resolved_voice_id and TTS_PROVIDER in {"edge_tts", "macos_say"}:
                resolved_voice_id = _default_voice_for_provider(
                    TTS_PROVIDER,
                    speaker,
                    guest.get("gender") or profile.get("gender", ""),
                    pid,
                )
            voices[speaker] = {
                "voice_id":           resolved_voice_id,
                "name":               guest.get("name", f"Guest {i + 1}"),
                "role":               guest.get("role", ""),
                "profile_id":         pid,
                "profile_description": profile.get("description", ""),
                "region":             profile.get("region", guest.get("region", "")),
                "pace":               profile.get("pace", guest.get("pace", "")),
                "energy":             profile.get("energy", guest.get("energy", "")),
                "vieneu_profile":     profile.get("vieneu_profile", ""),
                "pace_profile":       guest.get("pace_profile", profile.get("pace_profile", "")),
                "vieneu_request":     _merge_request_layers(
                    _voice_request_from_config(profile),
                    _resolve_vieneu_pace_request(guest.get("pace_profile", profile.get("pace_profile", ""))),
                    guest.get("vieneu_request", {}),
                ),
                "ref_audio":          guest_clone["ref_audio"] or profile_clone["ref_audio"],
                "ref_text":           guest_clone["ref_text"] or profile_clone["ref_text"],
                "ref_codes":          guest_clone["ref_codes"] if guest_clone["ref_codes"] is not None else profile_clone["ref_codes"],
                "selection_method":   method,
            }
        else:
            fallback_voice_id = ""
            if TTS_PROVIDER in {"edge_tts", "macos_say"}:
                fallback_voice_id = _default_voice_for_provider(
                    TTS_PROVIDER,
                    speaker,
                    guest.get("gender", ""),
                    guest.get("voice_profile", ""),
                )
            voices[speaker] = {
                "voice_id":         fallback_voice_id,
                "name":             guest.get("name", f"Guest {i + 1}"),
                "role":             guest.get("role", ""),
                "region":           guest.get("region", ""),
                "pace":             guest.get("pace", ""),
                "energy":           guest.get("energy", ""),
                "vieneu_profile":   guest.get("voice_profile", ""),
                "pace_profile":     guest.get("pace_profile", ""),
                "vieneu_request":   _merge_request_layers(
                    _resolve_vieneu_profile_request(guest.get("voice_profile", "")),
                    _resolve_vieneu_pace_request(guest.get("pace_profile", "")),
                    guest.get("vieneu_request", {}),
                ),
                "ref_audio":        guest_clone["ref_audio"],
                "ref_text":         guest_clone["ref_text"],
                "ref_codes":        guest_clone["ref_codes"],
                "selection_method": "none (no profiles configured)",
            }

    return voices


EPISODE = load_episode()
ACTIVE_VIENEU_ENGINE_MODE = resolve_vieneu_engine_mode(EPISODE)
VOICES  = resolve_all_voices(EPISODE)

# Print voice resolution summary
if not SUPPRESS_INIT_OUTPUT:
    print(f"\nTTS Provider : {TTS_PROVIDER.upper()} (requested: {REQUESTED_TTS_PROVIDER.upper()}, lang: {SCRIPT_LANGUAGE}, speed: {TARGET_PLAYBACK_SPEED:.2f}x)")
    if TTS_PROVIDER == "vieneu":
        print(f"VieNeu Engine : {ACTIVE_VIENEU_ENGINE_MODE}")
    for spk, info in VOICES.items():
        vid  = info.get("voice_id", "(missing)")
        name = info.get("name", "")
        how  = info.get("selection_method", "")
        vprof = info.get("vieneu_profile", "")
        prof = f"  [{info['profile_id']}]" if "profile_id" in info else ""
        profile_note = f"  tune={vprof}" if vprof else ""
        print(f"  {spk:<10} → {vid:<16} ({name}){prof}{profile_note}  via {how}")

_missing_voices = [spk for spk, info in VOICES.items() if not info.get("voice_id")]
if _missing_voices:
    if not SUPPRESS_INIT_OUTPUT:
        print(f"\nWARNING: missing voice_id for: {', '.join(_missing_voices)}")
        if TTS_PROVIDER == "elevenlabs":
            print("  → Fill elevenlabs_voice_id in voice_config.json for each speaker.")
        elif TTS_PROVIDER == "vieneu":
            print("  → Fill vieneu_voice_id in voice_config.json for each speaker.")
        else:
            print(f"  → For {TTS_PROVIDER}, set explicit voice IDs or configure community_tts.defaults.")

if TTS_PROVIDER == "elevenlabs" and not ELEVENLABS_API_KEY:
    if not SUPPRESS_INIT_OUTPUT:
        print("WARNING: TTS_PROVIDER=elevenlabs but ELEVENLABS_API_KEY is not set.")
    _missing_voices.append("ELEVENLABS_API_KEY")

AUDIO_ENABLED = not _missing_voices
VIENEU_FALLBACK_ENABLED = bool(VIENEU_FALLBACK_CFG.get("enabled", True))
VIENEU_FALLBACK_RETRY_ON_SLOW = bool(VIENEU_FALLBACK_CFG.get("retry_on_slow", True))
VIENEU_FALLBACK_SLOW_SECONDS = float(VIENEU_FALLBACK_CFG.get("slow_segment_seconds", 7.5))

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


# ── TTS: server management ───────────────────────────────────────────────────

def is_server_alive(url: str) -> bool:
    try:
        r = requests.get(f"{url}/health", timeout=1)
        if r.status_code != 200:
            return False
        return r.json().get("status") == "ok"
    except:
        return False


def get_server_health(url: str) -> dict:
    try:
        r = requests.get(f"{url}/health", timeout=2)
        if r.status_code != 200:
            return {}
        data = r.json()
        if not isinstance(data, dict):
            return {}
        return data
    except Exception:
        return {}


def get_server_engine_mode(url: str) -> str:
    global _SERVER_ENGINE_MODE
    info = get_server_health(url)
    raw_mode = str(info.get("engine_mode", "")).strip().lower()
    mode = raw_mode if raw_mode in {"standard", "turbo", "turbo_gpu"} else ""
    if mode:
        with _SERVER_ENGINE_LOCK:
            _SERVER_ENGINE_MODE = mode
        return mode
    with _SERVER_ENGINE_LOCK:
        return _SERVER_ENGINE_MODE


def set_server_engine_mode(url: str, mode: str) -> bool:
    global _SERVER_ENGINE_MODE
    normalized = _normalize_engine_mode(mode)
    if normalized not in {"standard", "turbo", "turbo_gpu"}:
        return False

    payload = {"engine_mode": normalized}
    try:
        r = requests.post(f"{url}/set_model", json=payload, timeout=30)
    except Exception as e:
        print(f"    ⚠ could not switch server engine to {normalized}: {e}")
        return False
    if r.status_code != 200:
        print(f"    ⚠ engine switch failed ({r.status_code}): {r.text[:180]}")
        return False
    with _SERVER_ENGINE_LOCK:
        _SERVER_ENGINE_MODE = normalized
    print(f"    Server engine switched to {normalized}")
    return True

def _warmup_vieneu_server() -> None:
    """Probe VieNeu /stream until the model is fully loaded and returns real audio.

    The /health endpoint reports the engine_mode as soon as the model switch is
    *initiated*, but the model can take 60–120 s to fully load.  Only a real
    /stream request tells us the model is warm.  We poll up to ~5 min (30 × 10 s).
    """
    probe_voice = next(iter(VOICES.values()), {}).get("voice_id", "") if VOICES else ""
    if not probe_voice:
        return
    probe_body = {
        "text": "Xin chào, đây là kiểm tra.",
        "voice": probe_voice,
        "render_mode": "stream",
    }
    print("    Warming up VieNeu model — waiting for first real audio response…")
    url = f"{VIENEU_URL}/stream"
    headers = {"Content-Type": "application/json"}
    for attempt in range(30):
        data = _post_with_retry(url, headers, probe_body, timeout=120)
        if data and len(data) >= 1024:
            print(f"    Model warm ✓ (attempt {attempt+1}, {len(data)} bytes)")
            return
        wait = 10
        print(f"    Warmup attempt {attempt+1}/30: model not ready ({len(data) if data else 0} bytes) — waiting {wait}s…")
        time.sleep(wait)
    print("    ⚠ Warmup did not confirm model ready after 5 min — proceeding anyway")


def ensure_tts_server():
    """Start local VieNeu-TTS server if it's selected and not running."""
    if TTS_PROVIDER != "vieneu":
        return

    print(f"  Checking VieNeu-TTS server at {VIENEU_URL}…")
    if is_server_alive(VIENEU_URL):
        running_mode = get_server_engine_mode(VIENEU_URL)
        if ACTIVE_VIENEU_ENGINE_MODE in {"standard", "turbo", "turbo_gpu"} and running_mode != ACTIVE_VIENEU_ENGINE_MODE:
            print(f"    Server running with engine={running_mode or 'unknown'}; switching to {ACTIVE_VIENEU_ENGINE_MODE}…")
            set_server_engine_mode(VIENEU_URL, ACTIVE_VIENEU_ENGINE_MODE)
            print(f"    Waiting for engine reload (max 60s)…")
            for _ in range(60):
                time.sleep(1)
                if get_server_engine_mode(VIENEU_URL) == ACTIVE_VIENEU_ENGINE_MODE:
                    print(f"    Engine ready: {ACTIVE_VIENEU_ENGINE_MODE} ✓")
                    break
            else:
                print(f"    ⚠ Engine switch not confirmed after 60s — proceeding anyway")
        print("    Server is already running ✓")
        _warmup_vieneu_server()
        return

    # Search for server script: first next to this file (skill scripts/), then walk up
    # to find it under .agents/skills/tech-radar-podcast/scripts/
    server_script = Path(__file__).parent / "vieneu_hq_server.py"
    if not server_script.exists():
        p = Path(__file__).parent
        for _ in range(8):
            p = p.parent
            candidate = p / ".agents" / "skills" / "tech-radar-podcast" / "scripts" / "vieneu_hq_server.py"
            if candidate.exists():
                server_script = candidate
                break
    if not server_script.exists():
        print(f"    ⚠ Server script not found — skipping auto-start")
        return

    print(f"    Server stopped — starting {server_script.name}…")
    # Use the VieNeu-TTS submodule venv from project root
    project_root = server_script.parent.parent.parent.parent.parent  # scripts/ → skill/ → skills/ → .agents/ → root
    venv_python = project_root / "VieNeu-TTS" / ".venv" / "bin" / "python"
    python_exec = str(venv_python) if venv_python.exists() else sys.executable
    if venv_python.exists():
        print(f"    Using venv interpreter: {python_exec}")

    log_path = Path("/tmp/tts_server.log")
    print(f"    Logging to {log_path}…")
    log_file = open(log_path, "w")

    env = os.environ.copy()
    env.setdefault("VIENEU_ENGINE_MODE", ACTIVE_VIENEU_ENGINE_MODE)

    subprocess.Popen(
        [python_exec, str(server_script)],
        stdout=log_file,
        stderr=log_file,
        start_new_session=True,
        env=env,
    )

    # Wait for ready
    print("    Waiting for model to load into GPU (max 180s)…")
    for _ in range(180):
        time.sleep(1)
        if is_server_alive(VIENEU_URL):
            get_server_engine_mode(VIENEU_URL)
            print("    Server ready! ✓")
            return
    print("    ⚠ Server failed to start within 180s — TTS requests might fail.")


# ── TTS: shared retry helper ──────────────────────────────────────────────────

def _post_with_retry(url: str, headers: dict, body: dict, timeout: int = 90) -> bytes | None:
    for attempt in range(3):
        try:
            r = requests.post(url, headers=headers, json=body, timeout=timeout)
            if r.status_code == 200:
                return r.content
            if r.status_code == 429:
                wait = int(r.headers.get("Retry-After", 15))
                print(f"    rate-limited — waiting {wait}s…")
                time.sleep(wait)
            else:
                print(f"    API error {r.status_code}: {r.text[:200]}")
                return None
        except Exception as e:
            print(f"    attempt {attempt + 1} failed: {e}")
            time.sleep(3)
    return None


def build_vieneu_request(seg: dict, speaker_info: dict, voice_id: str, text: str) -> dict:
    profile_name = seg.get("tts_profile") or speaker_info.get("vieneu_profile", "")
    pace_profile_name = seg.get("pace_profile") or speaker_info.get("pace_profile", "")
    profile_request = _resolve_vieneu_profile_request(profile_name)
    pace_request = _resolve_vieneu_pace_request(pace_profile_name)
    speaker_request = speaker_info.get("vieneu_request", {})
    request = _merge_request_layers(
        VIENEU_DEFAULT_REQUEST,
        speaker_request,
        profile_request,
        pace_request,
        seg.get("vieneu_request", {}),
    )
    request["text"] = text
    request["voice_id"] = voice_id or None

    seg_clone = _extract_clone_fields(seg)
    for key in ("ref_audio", "ref_text", "ref_codes"):
        value = speaker_info.get(key)
        if seg_clone.get(key):
            value = seg_clone.get(key)
        if value:
            request[key] = value

    request.setdefault("phonetic_normalize", False)
    return request


# ── TTS: VieNeu (local) ───────────────────────────────────────────────────────

def tts_vieneu(request_body: dict, out_path: Path) -> bool:
    """VieNeu-TTS streaming endpoint: POST /stream → streaming WAV → ffmpeg → MP3."""
    import subprocess, tempfile
    url     = f"{VIENEU_URL}/stream"
    headers = {"Content-Type": "application/json"}
    timeout = max(120, min(360, int(len(request_body.get("text", "")) * 0.45)))
    data    = _post_with_retry(url, headers, request_body, timeout=timeout)
    if not data or len(data) < 1024:
        if data:
            print(f"    ⚠ VieNeu returned suspicious {len(data)}-byte response — server may be reloading")
        return False
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(data)
        wav_path = f.name
    try:
        result = subprocess.run(
            [FFMPEG_BIN, "-y", "-i", wav_path, "-acodec", "libmp3lame", "-ab", OUTPUT_BITRATE, str(out_path)],
            capture_output=True, timeout=30,
        )
        return result.returncode == 0
    except Exception as e:
        print(f"    ffmpeg conversion failed: {e}")
        return False
    finally:
        os.unlink(wav_path)


# ── TTS: ElevenLabs (cloud) ───────────────────────────────────────────────────

def tts_elevenlabs(text: str, voice_id: str, out_path: Path) -> bool:
    """ElevenLabs TTS: POST /v1/text-to-speech/{voice_id} → MP3 directly."""
    if not ELEVENLABS_API_KEY:
        print("    ⚠ ELEVENLABS_API_KEY not set — skipping")
        return False
    url = f"{EL_API_URL}/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    body = {"text": text, "model_id": EL_MODEL, "voice_settings": EL_SETTINGS}
    data = _post_with_retry(url, headers, body, timeout=60)
    if data:
        out_path.write_bytes(data)
        return True
    return False


def tts_edge_tts(text: str, voice_id: str, out_path: Path) -> bool:
    """Free community TTS using edge-tts CLI."""
    if not EDGE_TTS_BIN:
        print("    ⚠ edge-tts not found in PATH")
        return False
    cmd = [
        EDGE_TTS_BIN,
        "--voice", voice_id,
        "--text", text,
        "--write-media", str(out_path),
    ]
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


def tts_macos_say(text: str, voice_id: str, out_path: Path) -> bool:
    """Offline free TTS using macOS say, then convert to MP3."""
    import tempfile
    if not SAY_BIN:
        print("    ⚠ macOS say not available")
        return False
    with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as f:
        aiff_path = f.name
    try:
        say_cmd = [SAY_BIN, "-v", voice_id, "-o", aiff_path, text]
        say_res = subprocess.run(say_cmd, capture_output=True, text=True, check=False)
        if say_res.returncode != 0:
            print(f"    say failed: {say_res.stderr[:200]}")
            return False

        conv = subprocess.run(
            [FFMPEG_BIN, "-y", "-i", aiff_path, "-acodec", "libmp3lame", "-ab", OUTPUT_BITRATE, str(out_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if conv.returncode != 0:
            print(f"    ffmpeg conversion failed after say: {conv.stderr[:200]}")
            return False
        return True
    except Exception as e:
        print(f"    say error: {e}")
        return False
    finally:
        if os.path.exists(aiff_path):
            os.unlink(aiff_path)


# ── TTS: provider dispatch ────────────────────────────────────────────────────

def tts(text: str, voice_id: str, out_path: Path, speaker_info: dict | None = None, seg: dict | None = None) -> tuple[bool, list[dict]]:
    if TTS_PROVIDER == "elevenlabs":
        t0 = time.time()
        ok = tts_elevenlabs(text, voice_id, out_path)
        return ok, [{"engine_mode": "elevenlabs", "ok": ok, "elapsed_s": round(time.time() - t0, 3)}]
    if TTS_PROVIDER == "edge_tts":
        t0 = time.time()
        ok = tts_edge_tts(text, voice_id, out_path)
        return ok, [{"engine_mode": "edge_tts", "ok": ok, "elapsed_s": round(time.time() - t0, 3)}]
    if TTS_PROVIDER == "macos_say":
        t0 = time.time()
        ok = tts_macos_say(text, voice_id, out_path)
        return ok, [{"engine_mode": "macos_say", "ok": ok, "elapsed_s": round(time.time() - t0, 3)}]

    request_body = build_vieneu_request(seg or {}, speaker_info or {}, voice_id, text)
    attempts: list[dict] = []

    current_mode = get_server_engine_mode(VIENEU_URL) or ACTIVE_VIENEU_ENGINE_MODE
    t0 = time.time()
    ok = tts_vieneu(request_body, out_path)
    elapsed = round(time.time() - t0, 3)
    attempts.append({"engine_mode": current_mode or "unknown", "ok": ok, "elapsed_s": elapsed})

    if not VIENEU_FALLBACK_ENABLED:
        return ok, attempts

    can_retry_turbo = (current_mode == "standard")
    if not can_retry_turbo:
        return ok, attempts

    retry_reason = ""
    if not ok:
        retry_reason = "failed"
    elif VIENEU_FALLBACK_RETRY_ON_SLOW and elapsed >= VIENEU_FALLBACK_SLOW_SECONDS:
        retry_reason = f"slow ({elapsed}s >= {VIENEU_FALLBACK_SLOW_SECONDS}s)"

    if not retry_reason:
        return ok, attempts

    print(f"    fallback trigger: {retry_reason} — retrying this segment in turbo")
    if not set_server_engine_mode(VIENEU_URL, "turbo"):
        return ok, attempts

    turbo_body = _merge_request_layers(request_body, VIENEU_TURBO_RETRY_REQUEST)
    turbo_out = out_path if not ok else out_path.with_suffix(".turbo_tmp.mp3")
    t1 = time.time()
    ok_turbo = tts_vieneu(turbo_body, turbo_out)
    elapsed_turbo = round(time.time() - t1, 3)
    attempts.append({"engine_mode": "turbo", "ok": ok_turbo, "elapsed_s": elapsed_turbo, "retry_reason": retry_reason})

    if ok and ok_turbo and turbo_out != out_path and turbo_out.exists():
        turbo_out.replace(out_path)
        return True, attempts
    if (not ok) and ok_turbo:
        return True, attempts
    if turbo_out != out_path and turbo_out.exists():
        turbo_out.unlink(missing_ok=True)
    return ok, attempts


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
        profile_label = seg.get("tts_profile") or info.get("vieneu_profile", "")
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
        if TTS_PROVIDER == "vieneu" and profile_label:
            print(f"  [{i+1:>3}/{len(speech_segs)}] {label} — profile {profile_label}")
        ok, attempts = tts(text, voice_id, out_path, info, seg)
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
        # Inter-segment cool-down: pause briefly between VieNeu inferences to reduce
        # MPS thermal throttle on Apple Silicon during long episode renders.
        if ok and TTS_PROVIDER == "vieneu" and VIENEU_INTER_SEG_SLEEP > 0:
            time.sleep(VIENEU_INTER_SEG_SLEEP)
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

    if TTS_PROVIDER == "vieneu":
        # VieNeu standard model on Apple Silicon (MPS) processes one request at a time.
        # Concurrency > 1 causes GPU contention, making each segment slower.
        max_workers = 1
    elif TTS_PROVIDER == "macos_say":
        max_workers = 2
    else:
        max_workers = 5

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
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
        "engine_mode_requested": ACTIVE_VIENEU_ENGINE_MODE if TTS_PROVIDER == "vieneu" else "",
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
            "vieneu_engine_mode": ACTIVE_VIENEU_ENGINE_MODE if TTS_PROVIDER == "vieneu" else "",
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

    print(f"\nTech Radar — Audio Production v6")
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

    print("\nPHASE C — TTS speech generation")
    ensure_tts_server()
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
        "vieneu_engine_mode": ACTIVE_VIENEU_ENGINE_MODE if TTS_PROVIDER == "vieneu" else "",
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
