# AI Daily Podcast — Phase Reference

All phases run in English. Phase 4 produces `script_en.txt` + `script_vi.txt`.

---

## PHASE 1 — BRIEFING

Parse the invocation. Infer:

| Field | What to extract | Fallback |
|-------|----------------|---------|
| `DATE` | Target date for the briefing | Today's date |
| `EPISODE_N` | Sequence number | Count existing `podcast_studio/daily_*` dirs + 1 |
| `DATE_SLUG` | Folder slug | `daily_[MMdd]` e.g. `daily_0403` for April 3 |
| `LANGUAGE` | Audio language | `vi` |

Create workspace and write `episode.json`:

```bash
DATE_SLUG=$(date +"%m%d")   # MMdd format, e.g. 0403 for April 3
WORKSPACE="./podcast_studio/daily_${DATE_SLUG}"
mkdir -p "${WORKSPACE}/research/raw" "${WORKSPACE}/logs" "${WORKSPACE}/exports" "${WORKSPACE}/cache/segments"
```

```python
import json, datetime

data = {
  "topic": f"AI daily briefing — {DATE}",
  "episode": EPISODE_N,
  "date": DATE,         # e.g. "April 3rd, 2026"
  "date_slug": DATE_SLUG,    # MMdd format, e.g. "0403"
  "language": "vi",
  "format": "solo",
  "duration_target_minutes": 20,
  "host_name": "Trung",
  "audience": "Engineering managers, product managers, AI solution builders",
  "voice_style": {
    "region": "south",
    "pace": "medium_fast",
    "energy": "warm_confident",
    "style": ["news", "analysis", "authoritative"]
  },
  "guests": []
}
open(f"{WORKSPACE}/episode.json", "w").write(json.dumps(data, indent=2, ensure_ascii=False))
```

Print briefing:
```
BRIEFING
Date:     [DATE]
Format:   Solo host — Trung
Language: vi
Target:   ~20 min (~3,800–4,200 spoken words)
Folder:   ./podcast_studio/daily_[DATE_SLUG]/
```

---

## PHASE 2 — RESEARCH

Spawn three subagents in parallel.

### Subagent A — Today's Hot Stories

```
You are a research assistant. Find the most important AI, tech, and business-of-AI
news published TODAY or in the last 24–48 hours (date: [DATE]).

Execute four searches:
1. "AI news today [DATE] major announcement release"
2. "AI funding acquisition product launch [DATE] site:techcrunch.com OR site:venturebeat.com"
3. "LLM model release benchmark [DATE]"
4. "AI enterprise deployment business [DATE] McKinsey Gartner Forrester"

For each story return a JSON object:
{
  "headline": "one-sentence headline",
  "source": "publication name",
  "url": "URL",
  "date": "publication date",
  "key_number": "the most important number or stat in this story",
  "why_it_matters": "2–3 sentences on competitive/technical significance",
  "audience_relevance": "manager" | "builder" | "both"
}

Return at least 6 stories. Return ONLY the JSON array.
```

### Subagent B — Signals & Trends

```
You are a research assistant. Search for emerging patterns, analyst forecasts,
and expert commentary published in the last 7 days (through [DATE]).

Execute three searches:
1. "AI trend signal forecast [this week/month] 2026 analyst report"
2. "AI startup ecosystem investment trend [DATE] site:crunchbase.com OR site:pitchbook.com"
3. "enterprise AI adoption challenge risk [DATE] Gartner Forrester IDC"

Return a JSON array:
[{
  "signal": "trend or pattern name",
  "evidence": "specific data point or quote",
  "implication": "what this means for managers and builders in the next 30–90 days",
  "source": "source name",
  "url": "URL"
}]

Return at least 4 signals. Return ONLY the JSON array.
```

### Subagent C — Challenges & Risks

```
You are a research assistant. Search for AI failures, risks, controversies,
and cautionary signals from the last 7 days (through [DATE]).

Execute two searches:
1. "AI failure risk security incident [DATE]"
2. "AI regulation policy concern criticism [DATE]"

Return a JSON array:
[{
  "challenge": "challenge title",
  "evidence": "specific incident or data point",
  "decision_implication": "what managers/builders should watch or change",
  "source": "source name",
  "url": "URL"
}]

Return at least 3 items. Return ONLY the JSON array.
```

Merge and save:

```json
{
  "date": "[DATE]",
  "stories": [ ...Subagent A... ],
  "signals": [ ...Subagent B... ],
  "challenges": [ ...Subagent C... ]
}
```

Save to: `./podcast_studio/daily_[DATE_SLUG]/research/research.json`

Minimum thresholds (run additional searches if below):
- Stories: ≥ 5 (with `key_number`)
- Signals: ≥ 3
- Challenges: ≥ 2

---

## PHASE 3 — CURATION

### Step 3a — Load Daily Series Memory

Before selecting stories, read `daily_series_context.json` to avoid covering the same ground:

```python
import json
from pathlib import Path

ctx_path = Path("./podcast_studio/daily_series_context.json")
ctx = json.loads(ctx_path.read_text()) if ctx_path.exists() else {}

recent_slugs   = {s["slug"] for s in ctx.get("covered_stories", [])}
open_forecasts = ctx.get("open_forecasts", [])   # may be empty initially
themes         = ctx.get("running_themes", [])

print("Recent daily slugs:", recent_slugs)
print("Open forecasts:", [f["text"] for f in open_forecasts])
```

Use this context when curating:
- **Skip or deprioritize** any story whose `slug` is in `recent_slugs` — unless there is a material update worth framing as a "Day N follow-up".
- **Check open forecasts**: if today's news confirms or refutes one, mark it for the script closing.
- **Reinforce or evolve** a running theme only if today's evidence genuinely adds new signal.

### Step 3b — Produce brief.md

Read `research.json`. Produce `brief.md` — the editorial backbone of the episode.

**Curation rules:**
1. Select the **top 3 stories** based on: impact + recency + relevance to managers/builders — excluding already-covered stories unless there is a meaningful update.
2. For each story, write a 2-sentence "analyst take": what does this mean for a decision this week?
3. Find the **cross-story theme**: what pattern does today's news collectively signal?
4. Write 2 **actionable takeaways** — one for managers, one for builders.
5. Identify 2 **unresolved questions** to close with — these may become `open_forecasts` in the series registry.

Save to: `./podcast_studio/daily_[DATE_SLUG]/brief.md`

```markdown
# Daily Brief — [DATE]

## Top 3 Stories

### 1. [Headline]
Source: [source] | Key number: [number]
Analyst take: [2 sentences — significance + decision implication]

### 2. [Headline]
...

### 3. [Headline]
...

## Cross-story theme
[2–3 sentences on the pattern connecting today's stories]

## Actionable takeaways
- Manager: [concrete action or watch item]
- Builder: [concrete action or build/defer decision]

## Closing questions
1. [Genuinely unresolved, no obvious answer]
2. [Genuinely unresolved, forward-looking]

## Sources used
[numbered list]
```

---

## PHASE 4 — SCRIPT

### Step 4a — Write English script

Follow [SCRIPT_GUIDE.md](SCRIPT_GUIDE.md). Save to `script_en.txt`.

Target: 2,800–3,400 English spoken words for ~20 min at medium-fast delivery.

Structure follows `brief.md` exactly — do not add new stories or themes not in the brief.

### Step 4b — Translate to Vietnamese

Translate to natural spoken Vietnamese following [VIETNAMESE_NOTES.md](VIETNAMESE_NOTES.md).

Save to `script_vi.txt`. Preserve all `[HOST]` and `[SEGMENT_BREAK]` markers.

### Step 4c — Verify

```bash
python3 << 'EOF'
import re, json
from pathlib import Path

ws = "./podcast_studio/daily_[DATE_SLUG]"
lang = json.loads(Path(f"{ws}/episode.json").read_text()).get("language", "vi")
sf = "script_vi.txt" if lang == "vi" else "script_en.txt"
script = Path(f"{ws}/{sf}").read_text()

lines = re.findall(r"^\[HOST\] (.+)", script, re.MULTILINE)
turns = len(lines)
words = sum(len(l.split()) for l in lines)
speed = 1.2 if lang == "vi" else 1.0
est_min_med = words / (140 * speed)
est_min_fast = words / (165 * speed)

print(f"Script: {sf}")
print(f"HOST turns: {turns}")
print(f"Spoken words: {words}")
print(f"Est duration: {est_min_fast:.1f}–{est_min_med:.1f} min")

dash_lines = [l[:80] for l in lines if re.search(r"—|-{1,2}(?!\d)", l)]
if dash_lines:
    print(f"WARNING: {len(dash_lines)} lines with dashes!")
    for d in dash_lines[:3]:
        print(f"  {d}")

if words < 3600 and lang == "vi":
    print("WARNING: word count below 3600 — expand 1–2 segments")
else:
    print("Word count: OK")
EOF
```

If under 3,600 words: expand the "Phân tích chủ đề" segment by 3–5 turns.

---

## PHASE 5 — AUDIO PRODUCTION

Ensure the VieNeu TTS server is running before this phase (required for `language=vi`):

```bash
# Check server health — must return {"status":"ok"}
curl http://127.0.0.1:8001/health

# If not running, start it:
python3 .agents/skills/tech-radar-podcast/scripts/vieneu_hq_server.py
```

For English episodes (`language=en` in `episode.json`), no local server is needed —
`produce_audio.py` uses `edge-tts` automatically with `macos-say` as fallback.

Run audio production:

```bash
python3 .agents/skills/tech-radar-podcast/scripts/produce_audio.py \
  --workspace "./podcast_studio/daily_[DATE_SLUG]"
```

`episode.json` has `"guests": []` — the renderer produces only HOST voice (Trung, VieNeu).

---

## PHASE 6 — VERIFY FINAL MP3

```bash
python3 -c "
from pydub import AudioSegment
import glob
files = glob.glob('./podcast_studio/daily_[DATE_SLUG]/exports/*_final.mp3')
if files:
    a = AudioSegment.from_mp3(files[0])
    print(f'Duration: {len(a)/60000:.1f} min | {files[0]}')
"
```

---

## PHASE 7 — DELIVERY REPORT

### Step 7a — Update Daily Series Memory

After the episode is complete, write to `podcast_studio/daily_series_context.json`. This file is owned exclusively by the daily series — no coordination with the weekly series needed.

```python
import json, re
from pathlib import Path
from datetime import date

ctx_path = Path("./podcast_studio/daily_series_context.json")
ctx = json.loads(ctx_path.read_text()) if ctx_path.exists() else {}
ctx.setdefault("covered_stories", [])
ctx.setdefault("open_forecasts", [])
ctx.setdefault("running_themes", [])

brief = Path("./podcast_studio/daily_[DATE_SLUG]/brief.md").read_text()

# --- 1. Register covered stories (keep last 30 = ~10 episodes) ---
new_stories = []
for line in re.findall(r"^### \d+\. (.+)", brief, re.MULTILINE):
    slug = re.sub(r"[^a-z0-9]+", "-", line.lower()).strip("-")[:60]
    new_stories.append({"slug": slug, "headline": line, "date": str(date.today())})

ctx["covered_stories"] = (new_stories + ctx["covered_stories"])[:30]

# --- 2. Close resolved forecasts; add new ones from "Closing questions" ---
resolved_slugs = set()  # fill manually if needed
ctx["open_forecasts"] = [f for f in ctx["open_forecasts"] if f["slug"] not in resolved_slugs]

new_q = re.findall(r"^\d+\. (.+)", brief.split("## Closing questions")[-1].split("##")[0], re.MULTILINE)
for q in new_q:
    slug = re.sub(r"[^a-z0-9]+", "-", q.lower()).strip("-")[:60]
    if slug not in {f["slug"] for f in ctx["open_forecasts"]}:
        ctx["open_forecasts"].append({"slug": slug, "text": q, "raised": str(date.today())})

ctx["open_forecasts"] = ctx["open_forecasts"][-10:]

# --- 3. Update running themes (keep last 5) ---
theme_match = re.search(r"## Cross-story theme\n(.+?)(?=\n##|\Z)", brief, re.DOTALL)
if theme_match:
    theme = theme_match.group(1).strip()
    ctx["running_themes"] = ([{"date": str(date.today()), "theme": theme}] + ctx["running_themes"])[:5]

ctx_path.write_text(json.dumps(ctx, ensure_ascii=False, indent=2))
print("Daily series context updated.")
```

### Step 7b — Delivery report

```
AI DAILY — EPISODE PRODUCTION COMPLETE
Date:      [DATE]
Episode:   #[N]
Format:    Solo host — Trung
Language:  vi
Duration:  [X] min
Script:    [N] words / [N] HOST turns

OUTPUT FILES
  brief.md             — curated story selection + analyst takes
  script_en.txt        — full English script
  script_vi.txt        — full Vietnamese script
  exports/             — final MP3
  daily_[MMdd]_vi_final.mp3        e.g. daily_0403_vi_final.mp3

TOP 3 STORIES (for show notes):
  1. [Headline — key number — source]
  2. [Headline — key number — source]
  3. [Headline — key number — source]

ANALYST THEME: [cross-story pattern in one sentence]
SERIES MEMORY: updated podcast_studio/daily_series_context.json
```
