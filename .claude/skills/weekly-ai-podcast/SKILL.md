---
name: weekly-ai-podcast
description: >
  Weekly AI briefing podcast production pipeline: research this week's biggest AI/tech/business
  stories → curate → script (EN + VI) → TTS → merged MP3. Two-host format with Trung and
  An. Audience: AI solution builders and engineering/product managers who need a sharp weekly
  synthesis plus forward-looking analysis. Produces "AI Weekly Radar" with a recurring host
  and guest. All research and scripting in English; audio in Vietnamese by default. Activate
  when the user requests: "tạo bản tin AI tuần này", "weekly AI podcast", "weekly-ai-podcast",
  "ai weekly radar", or any weekly AI news recap request.
license: MIT
compatibility: >
  Python 3.8+, ffmpeg, pip packages: edge-tts pydub.
metadata:
  author: h3tech
  version: "1.0"
  language: English (workflow) / Vietnamese + English (scripts)
allowed-tools: Bash Read Write WebSearch Agent
---

# AI Weekly Radar — Production Skill v1

Two-host weekly AI briefing for managers and builders. Pipeline:
**brief → research → curate → script (EN + VI) → TTS → merge**.
Run each phase immediately, print a summary, continue — no user confirmation needed.

**Format:** Two-host dialogue. Host = Trung (permanent). Guest = An (AI Market & Product Strategist, female).
**Target:** ~40-45 min Vietnamese audio (~8,500–9,500 spoken words, two-speaker total).
**Audience:** Engineering managers, product managers, AI solution builders.
**Angle:** Weekly recap + forward look. Not just "what happened this week" — always "what the week's pattern means for your next 2-4 weeks."
**Tone:** Conversational, debate-style, opinionated. Warm Southern Vietnamese register with natural miền Tây metaphors. Never corporate.

---

## ENVIRONMENT SETUP

Run once before producing any episode:

```bash
pip install edge-tts pydub audioop-lts --quiet
ffmpeg -version 2>/dev/null | head -1 || echo "WARNING: ffmpeg missing — brew install ffmpeg"
mkdir -p ./podcast_studio
```

All audio uses **edge-tts** (free, no local server needed). Voice assignment, pronunciation
normalization, pause tuning, and playback-speed defaults are centralized in `tech-radar-podcast`
and reused here; do not duplicate those rules in the weekly skill. The weekly format uses
`female_expert` for GUEST (An) — resolved automatically from `voice_profile: "auto"` in
`episode.json` based on gender and energy hints.

Shared assets (`produce_audio.py`, `voice_config.json`, `intro.mp3`, `outro.mp3`,
`transition.mp3`) live in the shared tech-radar skill directory. This skill reads
them in place — no duplication into episode workspaces.

---

## PHASE OVERVIEW

| # | Phase | Output |
|---|-------|--------|
| 1 | Briefing | `episode.json`, workspace dirs |
| 2 | Research | `research.json` — stories, signals, challenges, forward |
| 3 | Curation | `brief.md` — ranked stories + theme + creative module selection |
| 4 | Script | `script_en.txt` + `script_vi.txt` |
| 5 | Audio | `cache/segments/`, `exports/` |
| 6 | Merge | `exports/[slug]_vi_final.mp3` |
| 7 | Delivery | series context updated + **MP3 copied to `PODCAST_GDRIVE_PATH`** + delivery report |

Details: [PHASES.md](references/PHASES.md)

---

## DURATION HEURISTICS

**Target: 40-45 min Vietnamese audio at playback_speed=1.2 with two speakers**

| Pace band | Spoken words/min (2-speaker) | Words needed |
|-----------|------------------------------|--------------|
| Medium    | 130–140                      | 8,200–9,000  |
| Fast      | 155–170                      | 7,500–8,500  |

**Hard rule:** minimum **8,500 spoken words** (sum of all `[HOST]` + `[GUEST]` lines in `script_vi.txt`).
**Recommended:** 8,800–9,200 words with safety buffer.

Speed formula: `estimated_min = spoken_words / (145 × 1.2)`

---

## CREATIVE FORMAT PHILOSOPHY

The weekly format is **not a fixed 10-segment template**. Every episode has the same skeleton but the agent picks creative modules from a menu based on that week's news.

**Required skeleton (always):**
1. Cold Open — the week's defining number or claim
2. Week Recap — 3–5 top stories with dialogue analysis
3. Pattern Analysis — what the week collectively signals
4. Forward Look — what to watch in the next 2–4 weeks
5. Closing — 3 unresolved questions + resonant last line

**Optional modules (pick 2–3 per episode based on what fits):**
- `[MODULE: Forecast]` — base/bull/bear scenarios with % probability and triggers
- `[MODULE: Action Board]` — numbered actions for managers and builders separately
- `[MODULE: Myth vs Reality]` — 5–8 myth/reality pairs, rapid fire
- `[MODULE: CTO Decision Board]` — "if you're a CTO before 5PM today" rapid decisions
- `[MODULE: Hot Take Duel]` — HOST and GUEST take opposing sides on a controversial claim
- `[MODULE: Rebuttal Round]` — 4–5 common counterarguments + rebuttals
- `[MODULE: Decision Playbook]` — 5 decisions + 5 don'ts for next 2 weeks
- `[MODULE: Signal vs Noise]` — separate real signals from hype in 3–4 pairs

Details on each module: [SCRIPT_GUIDE.md](references/SCRIPT_GUIDE.md)

---

## SCRIPT FORMAT SUMMARY

Two-speaker dialogue. `[HOST]` leads, `[GUEST]` analyzes. Both are named in episode header.

```
TITLE: AI Weekly Radar — [natural date range]
SUBTITLE: [One sentence: the week's defining angle]
EPISODE: #[N] | [DATE] | Host: Trung & An (AI Market & Product Strategist)

[INTRO_MUSIC]

[HOST] [Cold open — number or claim, no greeting]
[GUEST] [First take]
...

[SEGMENT_BREAK: [Segment name]]

[HOST] / [GUEST] ...

[SEGMENT_BREAK: Closing]

[HOST] [3 closing questions as 3 consecutive HOST lines]
[GUEST] [Send-off — no sign-off phrase]
[HOST] [Final resonant line — no "see you next week"]

[OUTRO_MUSIC]

SOURCES:
1. [Source] — [URL] — [date] — cited for [fact]
```

Full script and spoken-text rules: [SCRIPT_GUIDE.md](references/SCRIPT_GUIDE.md)
Vietnamese translation rules: [VIETNAMESE_NOTES.md](references/VIETNAMESE_NOTES.md)

---

## RUN AUDIO PRODUCTION

Reuses tech-radar shared renderer:

```bash
WORKSPACE="./podcast_studio/weekly_[MMdd]"   # e.g. weekly_0406
python3 .agents/skills/tech-radar-podcast/scripts/produce_audio.py \
  --workspace "${WORKSPACE}"
```

---

## INVOCATION EXAMPLES

```
/weekly-ai-podcast
/weekly-ai-podcast tuần này
/weekly-ai-podcast week ending April 6
/ai-weekly-radar
tạo bản tin AI tuần này
weekly AI podcast
```

Date defaults to today (end of current week). Episode number auto-increments from existing `podcast_studio/weekly_*` folders.

---

## QUALITY CHECKLIST

**Script must have:**
- [ ] Cold open with a number or claim — no greeting
- [ ] ≥ 3 distinct weekly stories, each with dialogue analysis
- [ ] ≥ 1 cross-story "pattern" analysis
- [ ] 2–3 optional creative modules selected and clearly labeled
- [ ] Forward look: what to watch in 2–4 weeks
- [ ] ≥ 8 data points with specific numbers from research
- [ ] Total spoken words ≥ 8,500 (HOST + GUEST combined in VI script)
- [ ] 3 closing questions as consecutive [HOST] lines
- [ ] No dashes in spoken lines — TTS reads them aloud
- [ ] No markdown formatting in spoken lines
- [ ] Turn balance: GUEST turns ≥ 40% of total turns

**Script must NOT have:**
- [ ] "Xin chào", "Chào mừng", or any greeting
- [ ] ≥ 8 consecutive [HOST] or [GUEST] lines without a [SEGMENT_BREAK]
- [ ] "Cảm ơn đã lắng nghe", "Hẹn gặp lại tuần sau", or any sign-off
- [ ] Vague analysis without a concrete recommendation
- [ ] Same optional module two episodes in a row (vary the format)

**Analyst quality bar:**
Each story's analysis must answer at least one of:
- "Should I build on this / integrate this now or wait?"
- "Does this change my competitive position?"
- "What risk does this week's news create that I haven't priced in?"
- "What is the 2-4 week forward implication for my team?"

---

## DELIVERY CHECKLIST

**Every episode MUST complete all steps before reporting done:**

- [ ] `exports/[slug]_vi_final.mp3` exists and duration > 30 min
- [ ] `podcast_studio/weekly_series_context.json` updated with new stories + forecasts
- [ ] **MP3 copied to `PODCAST_GDRIVE_PATH`** (read from `.env`, run the copy command, confirm output)
- [ ] Delivery report printed with: duration, word count, stories covered, GDrive path

**Google Drive copy command (run this — do not skip):**
```bash
GDRIVE=$(grep '^PODCAST_GDRIVE_PATH=' .env 2>/dev/null | cut -d'=' -f2-)
FINAL_MP3=$(ls ./podcast_studio/weekly_*/exports/*_final.mp3 2>/dev/null | tail -1)
[ -d "$GDRIVE" ] && cp "$FINAL_MP3" "$GDRIVE/" && echo "✓ Copied: $(basename $FINAL_MP3) → $GDRIVE" || echo "WARNING: GDrive not mounted — copy manually: $FINAL_MP3"
```
