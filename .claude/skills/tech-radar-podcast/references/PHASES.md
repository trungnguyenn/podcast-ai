# Tech Radar — Phase Reference

Detailed instructions for all production phases. Read this when executing the podcast pipeline.

**All phases are conducted in English.** Phase 4 (Script) produces two output files:
`script_en.txt` (English original) and `script_vi.txt` (Vietnamese translation).

---

## PHASE 1 — BRIEFING

Parse the user's request. Never ask — infer from context:

| Field | What to extract | Fallback |
|-------|----------------|---------|
| `TOPIC` | Core subject matter | Required — no fallback |
| `GUESTS` | One or more guests (name, role, gender) | Single guest "Minh", infer role from topic |
| `LENGTH` | standard / deep-dive | standard (30 min) |
| `EPISODE_N` | Episode sequence number | 1 |
| `LANGUAGE` | Target audio language (en / vi) | vi |

**Guest role guide:**

| Topic area | Guest role | Preferred voice profile |
|-----------|-----------|------------------------|
| AI/ML models, LLMs | AI Research Engineer | `male_analytical` or `female_researcher` |
| Agentic coding, developer tools | Senior Software Engineer | `male_energetic` |
| Cloud infrastructure, K8s | Platform Engineer / SRE | `male_analytical` |
| Security, compliance | Security Architect | `male_analytical` or `female_expert` |
| Healthcare IT, EHR | Healthcare Informatics Specialist | `female_expert` |
| Business strategy, pricing | CTO / Product Director | `female_expert` or `male_analytical` |
| Data platforms, analytics | Data Platform Lead | `female_researcher` |
| Mobile, frontend | Senior Mobile Engineer | `male_energetic` |

**Voice profile selection:** Read `assets/voice_config.json`. Match topic first, then use any
available hints for region, pace, energy, and style to choose the best profile. Print the
selected profile ID so the user can set `GUEST_VOICE_PROFILE` before running audio production
if they want to override the automatic choice.

Create the episode workspace and print briefing:

```bash
SLUG=$(echo "[TOPIC]" | tr ' ' '_' | tr '[:upper:]' '[:lower:]' | cut -c1-40)
python3 .agents/skills/tech-radar-podcast/scripts/init_episode.py \
  --request "[ORIGINAL USER REQUEST]" \
  --topic "[TOPIC]" \
  --episode [N] \
  --language "[vi or en]"
echo "Output: ./podcast_studio/ep[N]_${SLUG}/"
```

Update `episode.json` inside the workspace so `produce_audio.py` can resolve voice profiles and script language:

```bash
python3 -c "
import json
data = {
  'topic': '[TOPIC]',
  'episode': [N],
  'date': '[DATE]',
  'language': '[vi or en]',
  'voice_style': {
    'region': '[north/south/central]',
    'pace': '[steady/medium/medium_fast/fast]',
    'energy': '[low_medium/warm_firm/high]',
    'style': ['[deep_dive]', '[debate]', '[business]']
  },
  'guests': [
    {
      'name': '[GUEST_1_NAME]',
      'role': '[GUEST_1_ROLE]',
      'gender': '[male/female]',
      'voice_profile': '[SELECTED_PROFILE_1 or auto]',
      'region': '[north/south/central]',
      'pace': '[steady/medium/medium_fast/fast]',
      'energy': '[low_medium/warm_firm/high]',
      'style': ['[deep_dive]', '[debate]']
    },
    {
      'name': '[GUEST_2_NAME]',
      'role': '[GUEST_2_ROLE]',
      'gender': '[male/female]',
      'voice_profile': '[SELECTED_PROFILE_2 or auto]'
    }
  ]
}
open('./podcast_studio/ep[N]_\${SLUG}/episode.json', 'w').write(json.dumps(data, indent=2, ensure_ascii=False))
print('episode.json written')
"
```

For a **single guest**, use a one-item array.

> [!IMPORTANT]
> **Always set `gender` for each guest.** If you are confident about the casting, set an explicit
> `'voice_profile'` such as `'male_analytical'` or `'female_expert'`. If you want the engine to choose,
> set `'voice_profile': 'auto'` and provide style hints like region, pace, and energy.

```
BRIEFING
Topic:          [TOPIC]
Language:       [vi / en]
Guests:         [GUEST_1_NAME] ([GUEST_1_ROLE]) — Gender: [M/F] → [SELECTED_PROFILE_1]
                [GUEST_2_NAME] ([GUEST_2_ROLE]) — Gender: [M/F] → [SELECTED_PROFILE_2]  (if multi-guest)
Length:         [LENGTH]
Episode:        #[N]
Folder:         ./podcast_studio/ep[N]_[slug]/
```

> [!TIP]
> **Voice Profile Selection:**
> - Female guest: prefer `female_expert` (healthcare/business) or `female_researcher` (technical).
> - Male guest: prefer `male_analytical` (leadership/technical) or `male_energetic` (startup/tools).
> If the script has a specific regional dialect or pacing requirement, fill in `region`, `pace`,
> `energy`, `style` in the guest or top-level `voice_style` to help the engine pick the right voice.

---

## PHASE 2 — PARALLEL RESEARCH

All research is conducted in English.

Spawn three subagents in parallel using the Agent tool.

### Subagent A — Facts & Statistics

```
You are a research assistant. Search for the most recent news, academic statistics, and consulting firm reports about: [TOPIC]

Execute four searches in sequence:
1. "[TOPIC] global market report 2025 2026 filetype:pdf"
2. "[TOPIC] statistics industry analysis Gartner McKinsey Forrester"
3. "[TOPIC] technical benchmarks comparison whitepaper"
4. "[TOPIC] revenue funding market size 2026 report"

Extract every concrete data point with a specific number, percentage, or measurable outcome.
Discard vague claims. Return a JSON array:
[
  {
    "fact": "one-sentence statement",
    "number": "the specific number or percentage",
    "source": "publication or organization (e.g. IDC, Statista, etc.)",
    "url": "URL if available",
    "date": "publication date if available"
  }
]
Return at least 8 items for deep-dive. Return ONLY the JSON array, no preamble.
```

### Subagent B — Case Studies & Expert Views

```
You are a research assistant. Search for real-world implementations and expert analysis of: [TOPIC]

Execute three searches:
1. "[TOPIC] implementation case study US enterprise Fortune 500 filetype:pdf"
2. "[TOPIC] US market adoption analysis Gartner Forrester prediction 2026"
3. "[TOPIC] competitive landscape US industry report 2026"

Return a JSON array:
[
  {
    "type": "case_study" or "expert_view",
    "entity": "company or person name",
    "finding": "what they did or said (detailed)",
    "outcome": "quantified result or key claim (must have numbers)",
    "source": "source name",
    "url": "URL if available"
  }
]
Return at least 5 items. Return ONLY the JSON array, no preamble.
```

### Subagent C — Challenges & Tensions

```
You are a research assistant. Search for problems, risks, and criticism of: [TOPIC]

Execute three searches:
1. "[TOPIC] challenges problems risks failure 2026"
2. "[TOPIC] criticism limitations downsides"
3. "[TOPIC] vs alternative comparison tradeoffs"

Return a JSON array:
[
  {
    "challenge": "challenge name or title",
    "evidence": "specific evidence or example",
    "tension": "why this creates genuine disagreement",
    "source": "source name",
    "url": "URL if available"
  }
]
Return at least 3 items. Return ONLY the JSON array, no preamble.
```

After all three complete, save merged research:

```json
{
  "facts":      [ ...Subagent A array... ],
  "cases":      [ ...Subagent B array... ],
  "challenges": [ ...Subagent C array... ]
}
```

Save merged research to: `./podcast_studio/ep[N]_[slug]/research/research.json`
Save raw subagent arrays to: `./podcast_studio/ep[N]_[slug]/research/raw/`

Verify counts:
```bash
python3 -c "
import json
d = json.load(open('./podcast_studio/ep[N]_[slug]/research/research.json'))
print(f\"facts={len(d['facts'])} cases={len(d['cases'])} challenges={len(d['challenges'])}\")
"
```

Print research summary — key facts, case studies, tensions, and regional angle.

Minimum thresholds (run additional searches if below):
- Facts with numbers: >= 6
- Case studies with quantified outcomes: >= 3
- Challenges: >= 3

---

## PHASE 3 — OUTLINE

All outlines are written in English.

Save to: `./podcast_studio/ep[N]_[slug]/outline.md`

```markdown
# Outline — Episode #[N]: [TITLE]

TARGET: 30 minutes (~4,500–6,000 spoken words for medium-fast English delivery, 50+ spoken turns)

INTRO:   Hook = [specific fact/claim/question to open with] — 5–8 turns
SEG 1:   "[NAME]" — Context & landscape — 8–10 turns — uses [which facts]
SEG 2:   "[NAME]" — Technical deep dive — 8–10 turns — uses [which case study]
SEG 3:   "[NAME]" — Real-world impact — 8–10 turns — HOST vs GUEST tension on [challenge]
SEG 4:   "[NAME]" — Business & market implications — 8–10 turns — US market focus
SEG 5:   "[NAME]" — Future outlook & Scaling — 6–8 turns — Fortune 500 adoption strategy
CLOSING: 3 unresolved questions + resonant final line — 5–7 turns
```

---

## PHASE 4 — SCRIPT

This phase produces **two script files**:

1. **`script_en.txt`** — The original English script, written following
   [SCRIPT_GUIDE.md](SCRIPT_GUIDE.md) for dialogue rules, natural conversation techniques,
   and spoken-text rules.

2. **`script_vi.txt`** — Vietnamese translation of the English script, adapted for natural
   spoken Vietnamese following [VIETNAMESE_NOTES.md](VIETNAMESE_NOTES.md).

### Step 4a — Write English script

Write the full English script following **[SCRIPT_GUIDE.md](SCRIPT_GUIDE.md)**.

Save to: `./podcast_studio/ep[N]_[slug]/script_en.txt`

> [!IMPORTANT]
> **For deep-dive (45+ min) episodes**, you **MUST** generate the script iteratively in parts:
> 1. Write `script_en.txt` containing INTRO + SEGMENT 1 & 2.
> 2. Append SEGMENT 3, 4, 5 + CLOSING in subsequent writes.
> Do not attempt to fit a deep-dive script into a single tool call!

### Step 4b — Translate to Vietnamese

Translate `script_en.txt` into natural spoken Vietnamese. This is NOT a literal translation.
Follow **[VIETNAMESE_NOTES.md](VIETNAMESE_NOTES.md)** for:
- Natural Vietnamese phrase palettes for HOST and GUEST
- Technical term adaptation rules
- Currency, percentage, date formatting for spoken Vietnamese
- Tone cue marker equivalents

Save to: `./podcast_studio/ep[N]_[slug]/script_vi.txt`

> [!IMPORTANT]
> The Vietnamese script must preserve the same structure (markers, segment breaks, number of
> turns) as the English original. Only the spoken text inside `[HOST]` and `[GUEST]` lines
> changes. All markers (`[INTRO_MUSIC]`, `[SEGMENT_BREAK: ...]`, etc.) stay identical.

### Step 4c — Verify both scripts

Run verification on the script that matches the target language in `episode.json`:

```bash
python3 << 'EOF'
import re, collections, json
from pathlib import Path

episode_path = Path("./podcast_studio/ep[N]_[slug]/episode.json")
lang = "vi"
if episode_path.exists():
    try:
        ep = json.loads(episode_path.read_text())
        lang = str(ep.get("language") or ep.get("lang") or "vi").lower()
    except Exception:
        lang = "vi"
if lang not in {"vi", "en"}:
    lang = "vi"

script_file = "script_vi.txt" if lang == "vi" else "script_en.txt"
script = open(f"./podcast_studio/ep[N]_[slug]/{script_file}").read()

spoken_lines = re.findall(r"^\[(?:HOST|GUEST(?:_\d+)?)\] (.+)", script, re.MULTILINE)
all_turns    = re.findall(r"^\[(HOST|GUEST(?:_\d+)?)\]", script, re.MULTILINE)
by_speaker   = collections.Counter(all_turns)
total_lines  = len(all_turns)
spoken_words = sum(len(l.split()) for l in spoken_lines)
has_tension  = bool(re.search(r"push back|disagree|challenge|but I think|however", script, re.I))
breakdown    = "  ".join(f"{spk}={n}" for spk, n in sorted(by_speaker.items()))

cfg_path = Path("./.agents/skills/tech-radar-podcast/assets/voice_config.json")
speed = 1.0
if cfg_path.exists():
    cfg = json.loads(cfg_path.read_text())
    audio_cfg = cfg.get("audio", {})
    speed_by_lang = audio_cfg.get("playback_speed_by_language", {})
    speed = float(speed_by_lang.get(lang, audio_cfg.get("playback_speed", 1.0)))
if speed <= 0:
    speed = 1.0

if lang == "vi":
    slow_range   = (spoken_words / (120 * speed), spoken_words / (100 * speed))
    med_range    = (spoken_words / (160 * speed), spoken_words / (130 * speed))
    fast_range   = (spoken_words / (200 * speed), spoken_words / (170 * speed))
else:
    slow_range   = (spoken_words / (140 * speed), spoken_words / (120 * speed))
    med_range    = (spoken_words / (170 * speed), spoken_words / (150 * speed))
    fast_range   = (spoken_words / (210 * speed), spoken_words / (180 * speed))

print(f"Script: {script_file}")
print(f"Spoken lines: {total_lines} ({breakdown})")
print(f"Spoken words: {spoken_words}")
print(f"Language: {lang} | playback_speed: {speed:.2f}x")
print(f"Est. duration (slow):   {slow_range[0]:.1f}–{slow_range[1]:.1f} min")
print(f"Est. duration (medium): {med_range[0]:.1f}–{med_range[1]:.1f} min")
print(f"Est. duration (fast):   {fast_range[0]:.1f}–{fast_range[1]:.1f} min")
print("Use medium-fast as the default Tech Radar band.")
print(f"Tension found: {has_tension}")

# TTS safety: detect dashes and markdown in spoken lines
dash_lines = [(i+1, l[:80]) for i, l in enumerate(spoken_lines) if re.search(r'—|-{1,2}(?!\d)', l)]
bold_lines = [(i+1, l[:80]) for i, l in enumerate(spoken_lines) if '**' in l or '__' in l]
if dash_lines:
    print(f"\nWARNING: {len(dash_lines)} spoken line(s) contain dashes — TTS will read them aloud!")
    for n, preview in dash_lines[:5]:
        print(f"  Line {n}: {preview}")
    print("  Fix: replace dashes with comma, ellipsis '...', or tone cue")
if bold_lines:
    print(f"\nWARNING: {len(bold_lines)} spoken line(s) contain markdown bold (**) — strip them!")

if total_lines < 50:
    print("\nWARNING: Script too short — need >= 50 spoken lines")
if spoken_words < 3500:
    print("WARNING: Word count too low — likely under-length")
EOF
```

If under 50 lines or 3,500 words, expand each segment by 2–4 additional exchanges.

---

## PHASE 5 — AUDIO PRODUCTION

Shared renderer path:

```bash
python3 -m py_compile ".agents/skills/tech-radar-podcast/scripts/produce_audio.py" \
  && echo "Syntax OK" || echo "Syntax error"
```

---

## PHASE 6 — RUN AUDIO

```bash
python3 .agents/skills/tech-radar-podcast/scripts/produce_audio.py \
  --workspace "./podcast_studio/ep[N]_[slug]"
```

The script reads `episode.json` to determine `language`, then loads the matching script file
(`script_vi.txt` for `vi`, `script_en.txt` for `en`). If the language-specific file is missing,
it falls back to `script.md` for backward compatibility.

If voice IDs are unknown, list available voices via your local VieNeu-TTS API:
```bash
# Example: curl -s "http://127.0.0.1:8001/v1/voices"
```

Verify final MP3:
```bash
python3 -c "
from pydub import AudioSegment
import glob
files = glob.glob('./podcast_studio/ep[N]_[slug]/exports/*_final.mp3')
if files:
    a = AudioSegment.from_mp3(files[0])
    print(f'Duration: {len(a)/60000:.1f} min | {files[0]}')
"
```

---

## PHASE 7 — DELIVERY REPORT

### Step 7a — Copy to Google Drive

After audio merge, copy the final MP3 to Google Drive. Read the path from `.env`:

```bash
GDRIVE=$(grep '^PODCAST_GDRIVE_PATH=' .env 2>/dev/null | cut -d'=' -f2-)
FINAL_MP3=$(ls ./podcast_studio/[WORKSPACE_SLUG]/exports/*_final.mp3 2>/dev/null | head -1)

if [ -z "$FINAL_MP3" ]; then
  echo "WARNING: No final MP3 found in exports/ — skipping Google Drive copy"
elif [ -z "$GDRIVE" ]; then
  echo "WARNING: PODCAST_GDRIVE_PATH not set in .env — skipping"
elif [ ! -d "$GDRIVE" ]; then
  echo "WARNING: Google Drive folder not mounted — skipping"
  echo "  Manually copy: $FINAL_MP3"
else
  cp "$FINAL_MP3" "$GDRIVE/" && echo "Copied to Google Drive: $(basename $FINAL_MP3)"
fi
```

### Step 7b — Delivery report

```
TECH RADAR — EPISODE PRODUCTION COMPLETE
Episode:   Episode #[N] — [TITLE]
Guest:     [GUEST_NAME], [GUEST_ROLE]
Language:  [vi / en]
Duration:  [X] minutes
Script:    [N] words / [N] spoken lines

OUTPUT FILES
  research.json       — sourced facts & cases
  outline.md          — episode structure (English)
  script_en.txt       — full English script with sources
  script_vi.txt       — full Vietnamese script (if language=vi)
  segments/           — individual TTS audio files
  cache/segments/     — derived speech cache
  exports/            — final rendered MP3s
  logs/               — render logs and phase events
  [slug]_final.mp3    — merged podcast episode
  manifest.json       — production log

Audio: [N]/[total] speech segments generated
Sources: [N] references cited

TOP 3 FACTS (for show notes):
  1. [Most striking data point — number — source]
  2. [Case study outcome — company — result]
  3. [Key tension — implication]
```
