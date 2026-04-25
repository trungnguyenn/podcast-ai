---
name: daily-ai-podcast
description: >
  Daily AI briefing podcast production pipeline: research today's hottest AI/tech/business
  news → curate → script (EN + VI) → TTS → merged MP3. Solo-host format (~20 min),
  no guest. Audience: AI solution builders and engineering/product managers who need
  sharp, actionable analysis of the day's AI landscape. Produces "AI Daily" with host
  Trung as permanent solo anchor. All research and scripting in English; audio in
  Vietnamese by default. Activate when the user requests: "tạo bản tin AI hôm nay",
  "daily AI podcast", "daily-ai-podcast", "cập nhật AI ngày [DATE]", or any daily
  AI news briefing request.
license: MIT
compatibility: >
  Python 3.8+, ffmpeg, pip packages: edge-tts pydub.
metadata:
  author: h3tech
  version: "1.0"
  language: English (workflow) / Vietnamese + English (scripts)
allowed-tools: Bash Read Write WebSearch Agent
---

# AI Daily Podcast — Production Skill v1

Solo-host daily AI briefing for managers and builders. Pipeline:
**brief → research → curate → script (EN + VI) → TTS → merge**.
Run each phase immediately, print a summary, continue — no user confirmation needed.

**Format:** Solo monologue with embedded analysis. No guest. Host = Trung (permanent).
**Target:** ~20 min Vietnamese audio (~3,600–4,200 spoken words).
**Audience:** Engineering managers, product managers, AI solution builders.
**Angle:** Not just "what happened" — always "what this means for your decisions this week."

---

## ENVIRONMENT SETUP

Run once before producing any episode:

```bash
pip install edge-tts pydub audioop-lts --quiet
ffmpeg -version 2>/dev/null | head -1 || echo "WARNING: ffmpeg missing — brew install ffmpeg"
mkdir -p ./podcast_studio
```

All audio uses **edge-tts** (free, no local server needed). Voice assignment, pronunciation
normalization, pause tuning, and playback-speed defaults are centralized in
`tech-radar-podcast` and reused here; do not duplicate those rules in the daily skill.

Shared assets (`produce_audio.py`, `voice_config.json`, `intro.mp3`, `outro.mp3`,
`transition.mp3`) live in the shared tech-radar skill directory. This skill reads
them in place — no duplication into episode workspaces.

---

## PHASE OVERVIEW

| # | Phase | Output |
|---|-------|--------|
| 1 | Briefing | `episode.json`, date slug |
| 2 | Research | `research.json` — hot stories, facts, signals |
| 3 | Curation | `brief.md` — ranked stories + analyst take |
| 4 | Script | `script_en.txt` + `script_vi.txt` |
| 5 | Audio | `cache/segments/`, `exports/` |
| 6 | Merge | `exports/[slug]_vi_final.mp3` |
| 7 | Delivery | series context updated + **MP3 copied to `PODCAST_GDRIVE_PATH`** + delivery report |

Details: [PHASES.md](references/PHASES.md)

---

## DURATION HEURISTICS

**Target: 20 min Vietnamese audio at playback_speed=1.2**

| Pace band | Spoken words/min | Words needed |
|-----------|-----------------|--------------|
| Slow      | 100–120         | 4,000–4,800  |
| Medium    | 130–150         | 3,600–4,200  |
| Fast      | 160–185         | 3,200–3,700  |

**Hard rule:** minimum **3,600 spoken words** for 20-min target.
**Recommended:** 3,800–4,200 words with safety buffer.

Speed formula: `estimated_min = spoken_words / (base_wpm × 1.2)`

---

## SCRIPT FORMAT

Solo monologue — only `[HOST]` spoken lines. No `[GUEST]`.

```
TITLE: AI Daily — [DATE in natural Vietnamese]
SUBTITLE: [One sentence: the angle that makes today's briefing worth 20 minutes]
EPISODE: #[N] | [DATE] | Host: Trung

[INTRO_MUSIC]

[HOST] Hook — first sentence is a number or a claim, never a greeting.

[SEGMENT_BREAK: Tin số 1 — [Story title]]

[HOST] ...

[SEGMENT_BREAK: Phân tích — [Theme]]

[HOST] ...

[SEGMENT_BREAK: Tín hiệu cho tuần tới]

[HOST] ...

[OUTRO_MUSIC]

SOURCES:
1. [Source] — [URL] — [date] — cited for [fact]
```

**Structure per story segment (3–4 turns of [HOST]):**
1. What happened (1 sentence, concrete number)
2. Why it matters technically / competitively
3. Analyst take: what managers/builders should do with this
4. Bridge to next story or theme

Full script and spoken-text rules: [SCRIPT_GUIDE.md](references/SCRIPT_GUIDE.md)

---

## EPISODE STRUCTURE

5 segments, tight pacing:

| Segment | Content | Turns |
|---------|---------|-------|
| INTRO hook | Opening bomb — one stat that defines the day | 2–3 |
| Tin số 1–3 | Top 3 stories, each with analyst take | 4–6 per story |
| Phân tích chủ đề | Cross-story pattern: what the day's news signals | 5–7 |
| Tín hiệu & Quyết định | Actionable takeaways for managers and builders | 4–5 |
| Kết | 2 unresolved questions + resonant close | 2–3 |

---

## RUN AUDIO PRODUCTION

Reuses tech-radar shared renderer:

```bash
WORKSPACE="./podcast_studio/daily_[MMdd]"   # e.g. daily_0403
python3 .agents/skills/tech-radar-podcast/scripts/produce_audio.py \
  --workspace "${WORKSPACE}"
```

---

## INVOCATION EXAMPLES

```
/ai-daily-podcast
/ai-daily-podcast ngày 3 tháng 4
/ai-daily-podcast April 3 2026
/ai-daily-podcast episode 5
```

Date defaults to today if not specified. Episode number auto-increments from existing `podcast_studio/daily_*` folders.

---

## QUALITY CHECKLIST

**Script must have:**
- [ ] Opening with a number or claim — no greeting
- [ ] ≥ 3 distinct news stories, each with analyst take
- [ ] ≥ 1 cross-story "pattern" analysis (the "so what" across all stories)
- [ ] ≥ 1 explicit "what managers should do" per story
- [ ] ≥ 1 explicit "what builders should do" per story  
- [ ] ≥ 6 data points with specific numbers from research
- [ ] spoken words ≥ 3,600 (Vietnamese)
- [ ] 2 closing questions that are genuinely unresolved
- [ ] No dashes in spoken lines — TTS reads them aloud
- [ ] No markdown formatting in spoken lines

**Script must NOT have:**
- [ ] "Xin chào", "Chào mừng", or any greeting
- [ ] ≥ 6 consecutive [HOST] lines without a [SEGMENT_BREAK]
- [ ] "Cảm ơn đã lắng nghe" or any sign-off
- [ ] Vague analysis without a concrete recommendation

**Analyst take quality bar:**
Each story's analysis must answer at least one of:
- "Should I build on this / integrate this now or wait?"
- "Does this change the competitive landscape I'm operating in?"
- "What risk does this create that I haven't priced in?"
- "What opportunity window does this open, and how long is it?"

---

## DELIVERY CHECKLIST

**Every episode MUST complete all steps before reporting done:**

- [ ] `exports/daily_[MMdd]_vi_final.mp3` exists and duration > 15 min
- [ ] `podcast_studio/daily_series_context.json` updated with new stories
- [ ] **MP3 copied to `PODCAST_GDRIVE_PATH`** (read from `.env`, run the copy command, confirm output)
- [ ] Delivery report printed with: duration, word count, stories covered, GDrive path

**Google Drive copy command (run this — do not skip):**
```bash
GDRIVE=$(grep '^PODCAST_GDRIVE_PATH=' .env 2>/dev/null | cut -d'=' -f2-)
FINAL_MP3=$(ls ./podcast_studio/daily_*/exports/*_final.mp3 2>/dev/null | tail -1)
[ -d "$GDRIVE" ] && cp "$FINAL_MP3" "$GDRIVE/" && echo "✓ Copied: $(basename $FINAL_MP3) → $GDRIVE" || echo "WARNING: GDrive not mounted — copy manually: $FINAL_MP3"
```
