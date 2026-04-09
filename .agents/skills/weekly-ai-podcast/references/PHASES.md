# AI Weekly Radar — Phase Reference

All phases run sequentially. Phase 4 produces `script_en.txt` (written first) then `script_vi.txt` (translated).

---

## PHASE 1 — BRIEFING

Parse the invocation. Infer:

| Field | What to extract | Fallback |
|-------|----------------|---------|
| `WEEK_END_DATE` | End date of the week being covered | Today's date |
| `EPISODE_N` | Sequence number | Count existing `podcast_studio/weekly_*` dirs + 1 |
| `DATE_SLUG` | Folder slug | `weekly_[MMdd]` e.g. `weekly_0406` for April 6 |
| `LANGUAGE` | Audio language | `vi` |

Create workspace and write `episode.json`:

```bash
DATE_SLUG="weekly_$(date +"%m%d")"   # e.g. weekly_0406
WORKSPACE="./podcast_studio/${DATE_SLUG}"
mkdir -p "${WORKSPACE}/research/raw" "${WORKSPACE}/logs" "${WORKSPACE}/exports" "${WORKSPACE}/cache/segments"
```

```python
import json, datetime

data = {
  "topic": f"Weekly AI Radar — week ending {WEEK_END_DATE}",
  "episode": EPISODE_N,
  "date": WEEK_END_DATE,
  "date_slug": DATE_SLUG,
  "language": "vi",
  "format": "weekly",
  "length": "standard",
  "duration_target_minutes": 42,
  "host_name": "Trung",
  "tone": "vui nhộn, gọn lịm miền Tây, gần gũi nhưng vẫn sắc bén cho manager/builder",
  "audience": "Engineering managers, product managers, AI solution builders",
  "voice_style": {
    "region": "south",
    "pace": "fast",
    "energy": "warm_confident",
    "style": ["debate", "forecast"]
  },
  "guests": [{
    "name": "An",
    "role": "AI Market & Product Strategist",
    "gender": "female",
    "voice_profile": "auto",
    "region": "south",
    "pace": "medium_fast",
    "energy": "warm_firm"
  }]
}
open(f"{WORKSPACE}/episode.json", "w").write(json.dumps(data, indent=2, ensure_ascii=False))
```

Print briefing:
```
BRIEFING
Week ending: [WEEK_END_DATE]
Format:      Two-host dialogue — Trung & An
Language:    vi
Target:      ~40-45 min (~8,500–9,200 spoken words)
Folder:      ./podcast_studio/[DATE_SLUG]/
```

---

## PHASE 2 — RESEARCH

Spawn **four subagents in parallel**.

### Subagent A — Weekly Top Stories

```
You are a research assistant. Find the most important AI, tech, and business-of-AI
news published in the LAST 7 DAYS (week ending [WEEK_END_DATE]).

Execute four searches:
1. "AI news [WEEK] major announcement release model launch"
2. "AI funding acquisition product launch [WEEK] site:techcrunch.com OR site:venturebeat.com"
3. "LLM model release benchmark [WEEK] 2026"
4. "AI enterprise deployment business strategy [WEEK] McKinsey Gartner Forrester"

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

Return at least 8 stories. Return ONLY the JSON array.
```

### Subagent B — Market Signals & Analyst Reports

```
You are a research assistant. Search for emerging patterns, analyst forecasts,
investment trends, and expert commentary from the LAST 7 DAYS (week ending [WEEK_END_DATE]).

Execute three searches:
1. "AI trend signal forecast [WEEK] 2026 analyst report Gartner Forrester McKinsey"
2. "AI startup funding investment round [WEEK] site:crunchbase.com OR site:pitchbook.com OR site:techcrunch.com"
3. "enterprise AI adoption challenge deployment [WEEK] survey report"

Return a JSON array:
[{
  "signal": "trend or pattern name",
  "evidence": "specific data point, number, or quote",
  "implication": "what this means for managers and builders in the next 30–90 days",
  "source": "source name",
  "url": "URL"
}]

Return at least 5 signals. Return ONLY the JSON array.
```

### Subagent C — Challenges, Risks & Controversies

```
You are a research assistant. Search for AI failures, risks, controversies,
regulatory moves, and cautionary signals from the LAST 7 DAYS (week ending [WEEK_END_DATE]).

Execute two searches:
1. "AI failure risk security incident controversy [WEEK] 2026"
2. "AI regulation policy law enforcement [WEEK] 2026 EU US"

Return a JSON array:
[{
  "challenge": "challenge or risk title",
  "evidence": "specific incident, stat, or quote",
  "decision_implication": "what managers/builders should watch or change",
  "source": "source name",
  "url": "URL"
}]

Return at least 3 items. Return ONLY the JSON array.
```

### Subagent D — Forward Signals (weekly-specific)

```
You are a research assistant. Search for upcoming AI events, release timelines,
executive commentary about near-term plans, and regulatory enforcement dates
relevant to the NEXT 2–4 WEEKS from [WEEK_END_DATE].

Execute two searches:
1. "AI upcoming release launch announced [NEXT_MONTH] 2026 expected"
2. "AI regulation enforcement date deadline [NEXT_MONTH] 2026 EU US"

Return a JSON array:
[{
  "signal": "what is coming or expected",
  "timeframe": "specific date or week window (e.g. 'by end of April 2026')",
  "trigger_to_watch": "the specific event or announcement that would confirm this signal",
  "source": "source name",
  "url": "URL"
}]

Return at least 3 items. Return ONLY the JSON array.
```

### Merge and Save

```json
{
  "week": "[WEEK_END_DATE]",
  "stories": [ ...Subagent A... ],
  "signals": [ ...Subagent B... ],
  "challenges": [ ...Subagent C... ],
  "forward": [ ...Subagent D... ]
}
```

Save to: `./podcast_studio/[DATE_SLUG]/research/research.json`

**Minimum thresholds** (run additional searches if below):
- Stories: ≥ 6 (with `key_number`)
- Signals: ≥ 4
- Challenges: ≥ 2
- Forward signals: ≥ 2

---

## PHASE 3 — CURATION

### Step 3a — Load Weekly Series Memory

Before selecting stories, read `weekly_series_context.json`. This file is owned exclusively by the weekly series — completely independent from daily episode runs.

```python
import json
from pathlib import Path

ctx_path = Path("./podcast_studio/weekly_series_context.json")
ctx = json.loads(ctx_path.read_text()) if ctx_path.exists() else {}
ctx.setdefault("covered_stories", [])
ctx.setdefault("open_forecasts", [])
ctx.setdefault("running_themes", [])

recent_slugs   = {s["slug"] for s in ctx["covered_stories"]}
open_forecasts = ctx["open_forecasts"]
themes         = ctx["running_themes"]

print("Recent weekly slugs:", recent_slugs)
print("Open forecasts:", [f["text"] for f in open_forecasts])
print("Running themes:", [t["theme"][:60] for t in themes])
```

Use this context when curating:
- **Skip or reframe** stories in `recent_slugs` — only cover if there is a meaningful development worth a "Last week we said X, this week Y happened" callback.
- **Evaluate open forecasts** from previous weekly episodes: did any resolve this week? Flag them as "resolved" or "still open" for the `[MODULE: Forecast Review]` segment.
- **Reinforce a running theme** only if this week's evidence meaningfully deepens it — avoid hollow callbacks.

### Step 3b — Produce brief.md

Read `research.json`. Produce `brief.md` — the editorial backbone of the episode.

**Curation rules:**
1. Select the **top 3–5 stories** based on: impact + recency + relevance to managers/builders — excluding already-covered weekly stories unless there is meaningful new development.
2. For each story, write a 2-sentence "analyst take": what does this mean for a decision this week?
3. Find the **cross-story theme**: what pattern does this week's news collectively signal?
4. Select **2–3 optional creative modules** from the menu below that best fit the week's theme. Justify why each was chosen. Include `Forecast Review` if there are ≥ 1 open forecasts from previous episodes.
5. Write 2 **actionable takeaways** — one for managers, one for builders.
6. Identify 3 **unresolved questions** to close with — these will become `open_forecasts` in the series registry.
7. List **forward signals** to incorporate into the Forward Look segment.

**Optional module selection guide:**
- Rich divergence of opinion this week → pick `Hot Take Duel` or `Rebuttal Round`
- Multiple strong analyst forecasts available → pick `Forecast` (base/bull/bear)
- Several recurring misconceptions visible in the week's coverage → pick `Myth vs Reality`
- Many discrete decisions needed this week → pick `Action Board` or `CTO Decision Board`
- Hard to separate real shifts from noise → pick `Signal vs Noise`
- Decision-dense week with 2-week horizon → pick `Decision Playbook`

Save to: `./podcast_studio/[DATE_SLUG]/brief.md`

```markdown
# Weekly Brief — [WEEK_END_DATE]

## Top Stories (selected)

### 1. [Headline]
Source: [source] | Key number: [number]
Analyst take: [2 sentences — significance + decision implication]

### 2. [Headline]
...

### 3–5. [additional stories]
...

## Cross-story theme
[2–3 sentences on the pattern connecting this week's stories]

## Selected creative modules (with rationale)
- [Module name]: [1 sentence why this fits this week]
- [Module name]: [1 sentence why this fits this week]
- [Module name]: [1 sentence why this fits this week]

## Forward signals to incorporate
[From Subagent D — list 2–3 most relevant]

## Actionable takeaways
- Manager: [concrete action or watch item]
- Builder: [concrete action or build/defer decision]

## Closing questions
1. [Genuinely unresolved, no obvious answer]
2. [Genuinely unresolved, forward-looking]
3. [Genuinely unresolved, structural/long-horizon]

## Sources used
[numbered list]
```

---

## PHASE 4 — SCRIPT

### Step 4a — Write English script

Follow [SCRIPT_GUIDE.md](SCRIPT_GUIDE.md). Save to `script_en.txt`.

Target: **6,500–7,500 English spoken words** for ~40-45 min at two-speaker medium-fast pace.

Structure follows `brief.md` exactly — do not add new stories or themes not in the brief.

Required skeleton segments + selected modules from `brief.md`.

### Step 4b — Translate to Vietnamese

Translate to natural spoken Vietnamese following [VIETNAMESE_NOTES.md](VIETNAMESE_NOTES.md).

Save to `script_vi.txt`. Preserve all `[HOST]`, `[GUEST]`, and `[SEGMENT_BREAK]` markers exactly.

Vietnamese naturally expands vs English — expect 10–20% more words. This is expected and desirable for the word count target.

### Step 4c — Verify

```bash
python3 << 'EOF'
import re, json
from pathlib import Path

ws = "./podcast_studio/[DATE_SLUG]"
lang = json.loads(Path(f"{ws}/episode.json").read_text()).get("language", "vi")
sf = "script_vi.txt" if lang == "vi" else "script_en.txt"
script = Path(f"{ws}/{sf}").read_text()

host_lines   = re.findall(r"^\[HOST\] (.+)", script, re.MULTILINE)
guest_lines  = re.findall(r"^\[GUEST\] (.+)", script, re.MULTILINE)
all_spoken   = host_lines + guest_lines
total_turns  = len(host_lines) + len(guest_lines)
words        = sum(len(l.split()) for l in all_spoken)
host_pct     = len(host_lines) / total_turns * 100 if total_turns else 0
guest_pct    = len(guest_lines) / total_turns * 100 if total_turns else 0
speed        = 1.2 if lang == "vi" else 1.0
est_min_med  = words / (140 * speed)
est_min_fast = words / (165 * speed)

print(f"Script:       {sf}")
print(f"HOST turns:   {len(host_lines)} ({host_pct:.0f}%)")
print(f"GUEST turns:  {len(guest_lines)} ({guest_pct:.0f}%)")
print(f"Total turns:  {total_turns}")
print(f"Spoken words: {words}")
print(f"Est duration: {est_min_fast:.1f}–{est_min_med:.1f} min")

dash_lines = [l[:80] for l in all_spoken if re.search(r"—|-{1,2}(?!\d)", l)]
if dash_lines:
    print(f"WARNING: {len(dash_lines)} lines with dashes!")
    for d in dash_lines[:3]:
        print(f"  {d}")
else:
    print("Dash check:   OK")

if guest_pct < 40:
    print(f"WARNING: GUEST share {guest_pct:.0f}% is below 40% — expand GUEST turns")
else:
    print(f"Turn balance: OK")

if words < 8500 and lang == "vi":
    print("WARNING: word count below 8500 — expand 2–3 segments")
else:
    print("Word count:   OK")
EOF
```

If under 8,500 words: expand the Pattern Analysis segment and one optional module by 4–6 turns each.
If GUEST share below 40%: add GUEST analysis turns to the Pattern Analysis and Forward Look segments.

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
HOST maps to `en-US-AndrewMultilingualNeural`, GUEST to `en-US-AvaMultilingualNeural`
(female, matching An's `gender: female` profile).

Run audio production:

```bash
python3 .agents/skills/tech-radar-podcast/scripts/produce_audio.py \
  --workspace "./podcast_studio/[DATE_SLUG]"
```

`episode.json` has `"guests": [{ "name": "An", "gender": "female", "voice_profile": "auto", ... }]`
— the renderer produces HOST voice (Trung) and GUEST voice (An, auto-resolved to `female_expert`
profile: VieNeu voice `Doan` for VI, `en-US-AvaMultilingualNeural` for EN).

---

## PHASE 6 — VERIFY FINAL MP3

```bash
python3 -c "
from pydub import AudioSegment
import glob
files = glob.glob('./podcast_studio/[DATE_SLUG]/exports/*_final.mp3')
if files:
    a = AudioSegment.from_mp3(files[0])
    print(f'Duration: {len(a)/60000:.1f} min | {files[0]}')
else:
    print('No final MP3 found')
"
```

---

## PHASE 7 — DELIVERY REPORT

### Step 7a — Update Weekly Series Memory

After the episode is complete, write to `podcast_studio/weekly_series_context.json`. This file is owned exclusively by the weekly series — no coordination with the daily series needed.

```python
import json, re
from pathlib import Path
from datetime import date

ctx_path = Path("./podcast_studio/weekly_series_context.json")
ctx = json.loads(ctx_path.read_text()) if ctx_path.exists() else {}
ctx.setdefault("covered_stories", [])
ctx.setdefault("open_forecasts", [])
ctx.setdefault("running_themes", [])

brief = Path("./podcast_studio/[DATE_SLUG]/brief.md").read_text()

# --- 1. Register covered stories (keep last 25 = ~5 weeks) ---
new_stories = []
for line in re.findall(r"^### \d+\. (.+)", brief, re.MULTILINE):
    slug = re.sub(r"[^a-z0-9]+", "-", line.lower()).strip("-")[:60]
    new_stories.append({"slug": slug, "headline": line, "date": str(date.today())})

ctx["covered_stories"] = (new_stories + ctx["covered_stories"])[:25]

# --- 2. Close forecasts resolved this week; add new ones from "Closing questions" ---
# Fill resolved_slugs from the [MODULE: Forecast Review] segment produced this episode.
resolved_slugs = set()  # e.g. {"gpt-5-release-date-q2-2026"}
ctx["open_forecasts"] = [f for f in ctx["open_forecasts"] if f["slug"] not in resolved_slugs]

new_q_section = brief.split("## Closing questions")[-1].split("##")[0] if "## Closing questions" in brief else ""
for q in re.findall(r"^\d+\. (.+)", new_q_section, re.MULTILINE):
    slug = re.sub(r"[^a-z0-9]+", "-", q.lower()).strip("-")[:60]
    if slug not in {f["slug"] for f in ctx["open_forecasts"]}:
        ctx["open_forecasts"].append({"slug": slug, "text": q, "raised": str(date.today())})

ctx["open_forecasts"] = ctx["open_forecasts"][-10:]

# --- 3. Update running themes (keep last 5 weeks) ---
theme_match = re.search(r"## Cross-story theme\n(.+?)(?=\n##|\Z)", brief, re.DOTALL)
if theme_match:
    theme = theme_match.group(1).strip()
    ctx["running_themes"] = ([{"date": str(date.today()), "theme": theme}] + ctx["running_themes"])[:5]

ctx_path.write_text(json.dumps(ctx, ensure_ascii=False, indent=2))
print("Weekly series context updated.")
```

### Step 7b — Delivery report

```
AI WEEKLY RADAR — EPISODE PRODUCTION COMPLETE
Week ending: [WEEK_END_DATE]
Episode:     #[N]
Format:      Two-host — Trung & An
Language:    vi
Duration:    [X] min
Script:      [N] words / [N] HOST turns / [N] GUEST turns

OUTPUT FILES
  brief.md              — curated story selection + module plan
  script_en.txt         — full English script
  script_vi.txt         — full Vietnamese script
  exports/              — final MP3
  [DATE_SLUG]_vi_final.mp3

TOP STORIES (for show notes):
  1. [Headline — key number — source]
  2. [Headline — key number — source]
  3. [Headline — key number — source]

WEEK THEME: [cross-story pattern in one sentence]
MODULES USED: [list of optional modules chosen]
FORWARD WATCH: [top 1–2 signals for next 2-4 weeks]
SERIES MEMORY: updated podcast_studio/weekly_series_context.json
```
