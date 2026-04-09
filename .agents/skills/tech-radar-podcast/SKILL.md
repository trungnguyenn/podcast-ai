---
name: tech-radar-podcast
description: >
  Full end-to-end tech podcast production pipeline: research → outline → script → TTS
  audio → fixed assets → merged MP3. Produces "Tech Radar" with a permanent host (Trung)
  and one or more guest experts per episode. All workflow steps (research, outline, script)
  are conducted in English. The script phase produces two versions: script_en.txt (original
  English) and script_vi.txt (Vietnamese translation). Audio production picks the right
  script based on episode.json language setting (default: Vietnamese). Uses VieNeu-TTS for
  Vietnamese speech, edge-tts/macos-say for English; intro, outro, and transitions are
  fixed MP3 assets. Activate when the user requests: "create podcast about X",
  "make episode about Y", "record podcast X", or any podcast production request with a
  technology topic.
license: MIT
compatibility: >
  Python 3.8+, ffmpeg, pip packages: requests pydub. Local VieNeu-TTS API server must be running for Vietnamese episodes. macOS and Linux supported.
metadata:
  author: h3tech
  version: "4.0"
  language: English (workflow) / Vietnamese + English (scripts)
allowed-tools: Bash Read Write WebSearch Agent
---

# Tech Radar Podcast — Production Skill v4

Full-stack podcast producer for "Tech Radar". Execute the complete pipeline autonomously:
**plan → research → outline → script (EN + VI) → TTS → merge**. Announce each phase,
execute it, print a brief summary, then continue immediately — no waiting for user
confirmation.

**Key principle:** All workflow steps are in English. The script phase always produces two
versions — an English original (`script_en.txt`) and a Vietnamese translation
(`script_vi.txt`). Audio production selects the appropriate script based on the `language`
field in `episode.json` (default: `vi`).

---

## ENVIRONMENT SETUP

Run once before any episode:

```bash
python3 -c "import requests, pydub; print('deps: OK')" 2>/dev/null \
  || pip install requests pydub --quiet
python3 -c "import audioop" 2>/dev/null \
  || pip install audioop-lts --quiet
ffmpeg -version 2>/dev/null | head -1 \
  || echo "WARNING: ffmpeg missing — brew install ffmpeg"
echo "VieNeu URL=${VIENEU_URL:-http://127.0.0.1:8001}"
mkdir -p ./podcast_studio
```

**Voice config — stored in `assets/voice_config.json`:**
| Env var | Description |
|---------|-------------|
| `TTS_PROVIDER` | `auto` (default), `vieneu`, `edge_tts`, `macos_say`, or `elevenlabs` |
| `VIENEU_URL` | Override local VieNeu-TTS server URL |
| `ELEVENLABS_API_KEY` | Required for ElevenLabs provider |
| `HOST_VOICE_ID` | Override host voice ID |
| `GUEST_VOICE_ID` | Override first guest voice ID |
| `GUEST_VOICE_PROFILE` | Force a specific profile for first guest |
| `GUEST_2_VOICE_ID` | Override second guest voice ID |
| `GUEST_2_VOICE_PROFILE` | Force a specific profile for second guest |

**Guest voices are auto-selected** from `voice_config.json` using topic, plus any available hints for
region, pace, energy, and style written into `episode.json`. When multiple guests are present, each gets
a **different** profile when possible. No manual `export` needed — `produce_audio.py` handles all
resolution and prints the chosen voice plus VieNeu tuning profile at startup.

**Provider auto-routing (default):**
- English script (`language=en` in episode.json): `edge_tts` first, fallback `macos_say`
- Vietnamese script (`language=vi` in episode.json, or unset): `vieneu`

**Edit `assets/voice_config.json` to configure voices, VieNeu engine strategy in
`vieneu.engine.mode` (`standard`, `turbo`, `turbo_gpu`, `auto`), fallback policy in
`vieneu.fallback_standard_to_turbo`, base request tuning in `vieneu.default_request`, per-profile
tuning in `vieneu.profiles`, pace tuning in `vieneu.pace_profiles`, `tts_polish`, adaptive pause
rules, loudness normalization, final `audio.playback_speed` (default `1.2`), and
`phonetic_normalization` (to fix pronunciation like "AI" or ".com" without restarting the server).**
See [references/AUDIO_GUIDE.md](references/AUDIO_GUIDE.md) for full audio documentation.

---

## PHASE OVERVIEW

| # | Phase | Language | Output | Reference |
|---|-------|----------|--------|-----------|
| 1 | Briefing | English | Episode params + voice profile | [PHASES.md §1](references/PHASES.md) |
| 2 | Research | English | `research.json` (facts, cases, challenges) | [PHASES.md §2](references/PHASES.md) |
| 3 | Outline | English | `outline.md` | [PHASES.md §3](references/PHASES.md) |
| 4 | Script | EN + VI | `script_en.txt` + `script_vi.txt` | [PHASES.md §4](references/PHASES.md) + [SCRIPT_GUIDE.md](references/SCRIPT_GUIDE.md) |
| 5 | Audio production | — | `cache/segments/`, `exports/` | [AUDIO_GUIDE.md](references/AUDIO_GUIDE.md) |
| 6 | Merge | — | `exports/[slug]_[lang]_final.mp3` | [AUDIO_GUIDE.md](references/AUDIO_GUIDE.md) |
| 7 | Delivery report | English | `manifest.json`, `workspace_manifest.json`, `status.json` | [PHASES.md §7](references/PHASES.md) |

---

## DURATION HEURISTICS

### English scripts

| Pace | Words / minute | Typical style |
|------|----------------|---------------|
| Slow | 120–140 | Careful, academic, explanatory |
| Medium | 150–170 | Conversational, analytical |
| Fast | 180–210+ | Podcast, debate, high-energy talk show |

**Default for Tech Radar English:** assume **medium-fast delivery**.
- Standard 25–35 min episodes: ~4,500–6,000 spoken words
- Deep-dive 45–50 min episodes: ~7,500–9,500 spoken words

### Vietnamese scripts

**IMPORTANT:** Do **not** estimate Vietnamese duration using English WPM rates.
Vietnamese TTS often speaks faster than expected (especially with `playback_speed=1.2`), so naive word targets can under-run by 20-35%.

| Pace | Spoken words / minute | Typical style |
|------|------------------------|---------------|
| Slow | 100–120 | Careful, academic, explanatory |
| Medium | 130–150 | Conversational, analytical |
| Fast | 160–185 | Podcast, debate, high-energy talk show |

**Default for Tech Radar Vietnamese:** assume **effective medium-fast** with safety buffer.
- 30-minute target episode: **minimum 5,400 spoken words** (recommended 5,600–6,200)
- Standard 25–35 min episodes: ~5,200–6,800 spoken words
- Deep-dive 45–50 min episodes: ~8,000–10,000 spoken words

**Hard rule for VI 30-minute requests:** never finalize below **5,400 spoken words** unless pilot-audio projection proves >=30:00.

### Speed-adjusted duration formula (required)

- `effective_wpm = base_wpm * playback_speed`
- `estimated_minutes = spoken_words / effective_wpm`

Current defaults:
- Vietnamese (`vi`) uses `playback_speed=1.2` — duration estimates should be shorter.
- English (`en`) uses `playback_speed=1.0` — duration estimates unchanged.

When verifying a script, **print a duration range** across pace bands instead of a single estimate.

### Anti-underestimate guardrail (required)

Before finalizing script length, run this 3-step calibration:

1. **Word-count gate**
   - Compute spoken words from `[HOST]/[GUEST*]` lines only.
   - If `language=vi` and target is 30 min: require `spoken_words >= 5400`.

2. **Pilot audio projection**
   - Render the first 24 spoken turns to temporary segments.
   - Measure `avg_seconds_per_spoken_turn`.
   - Project full duration: `projected_minutes = (avg_seconds_per_spoken_turn * total_spoken_turns) / 60`.

3. **Safety margin**
   - Do not stop at 30.0 exactly.
   - Require projected duration >= `target_minutes * 1.08` before final audio render (for 30 min target, project at least **32.4 min**).
   - If below threshold, append one more script chunk (15-25 turns), then re-project.

---

## SCRIPT FORMAT (.txt)

Scripts use plain text with line-based markers — not markdown. The parser reads each line
and matches markers via regex. Anything that is not a recognized marker is ignored.

### Recognized markers

| Marker | Audio result |
|--------|-------------|
| `[HOST] text` | TTS with host voice (Trung) |
| `[GUEST] text` | TTS with first guest voice |
| `[GUEST_2] text` | TTS with second guest voice |
| `[GUEST_3] text` | TTS with third guest voice (and so on) |
| `[INTRO_MUSIC]` | Fixed `assets/intro.mp3` |
| `[OUTRO_MUSIC]` | Fixed `assets/outro.mp3` |
| `[SEGMENT_BREAK: Title]` | Fixed `assets/transition.mp3` + optional HOST title announcement |
| `[SOUND_EFFECT: label]` | Fixed `assets/transition.mp3` (label is informational) |
| `[laugh]` / `[pause]` / `[serious]` | Tone cues — stripped before TTS, no audio |

`[GUEST]` and `[GUEST_1]` are identical — both map to the first guest. Use `[GUEST]` for single-guest episodes.

### Script file layout

```
TITLE: [Episode title]
SUBTITLE: [One sentence that sharpens the angle]
EPISODE: #[N] | [DATE] | Host: Trung & [GUEST_NAME] ([GUEST_ROLE])

[INTRO_MUSIC]

[HOST] Opening line — immediate impact, no pleasantries.

[GUEST] Reaction and guest angle.

[SEGMENT_BREAK: Segment 1 — Title]

[HOST] ...
[GUEST] ...

[SEGMENT_BREAK: Closing]

[HOST] Open question with no easy answer.

[OUTRO_MUSIC]

SOURCES:
1. [Source name] — [URL] — [date] — cited for [fact]
```

No markdown headings, bold, horizontal rules, or tables inside the script body.
Metadata (title, subtitle, episode info) uses plain `KEY: value` lines at the top.
Sources use a numbered list at the bottom.

---

## GUEST VOICE SELECTION (Phase 1)

**Auto-selection is handled by `produce_audio.py`** — it reads the topic from `episode.json`
and combines it with `gender`, `region`, `pace`, `energy`, and `style` hints when present.
If you want the engine to choose, set `voice_profile` to `auto`; if you already know the right
casting, set an explicit profile.

During Phase 1 you must write `episode.json` (see PHASES.md §1). The table below is for
reference only, to confirm what auto-select will pick:

| Topic domain | Auto-selected profile |
|-------------|----------------------|
| AI/ML, LLMs, cloud, security | `male_analytical` or `female_researcher` |
| Developer tools, startup, product | `male_energetic` |
| Healthcare, compliance, legal | `female_expert` |
| Business strategy, executive | `male_analytical` or `female_expert` |
| Data platforms, analytics | `female_researcher` or `male_analytical` |

If the guest character is female, adjust guest name accordingly — the auto-select will
prefer female profiles when topic matches `female_*` profiles better.

---

## RUN AUDIO PRODUCTION

```bash
WORKSPACE="./podcast_studio/ep[N]_[slug]"
python3 .agents/skills/tech-radar-podcast/scripts/produce_audio.py --workspace "${WORKSPACE}"
```

The renderer now runs from the shared skill directory. It reads shared code and fixed assets
in place, and writes only episode-owned artifacts into the workspace under `podcast_studio/`.
It selects `script_vi.txt` or `script_en.txt` based on the `language` field in `episode.json`
(default: `vi`).

For performance tuning, run:

```bash
python3 .agents/skills/tech-radar-podcast/scripts/produce_audio.py \
  --workspace "./podcast_studio/ep[N]_[slug]" \
  --benchmark
```

This generates `benchmark_report.json` with per-segment latency and RTF.

---

## INVOCATION EXAMPLES

```
/tech-radar-podcast Claude Code 2.1 and the future of autonomous software development
/tech-radar-podcast HIPAA compliance when using AI agents in US healthcare
/tech-radar-podcast H3Tech: transitioning business model from software services to AI-native
/tech-radar-podcast agentic AI in revenue cycle management at US hospitals
```

Override defaults inline:
- `"... deep-dive"` → 45–50 min, ≥ 120 spoken turns
  *(CRITICAL: For deep-dive episodes, you MUST generate the script iteratively in multiple chunks/appends (e.g., 3-4 generations). A single generation will truncate and result in a <30 min script.)*
- `"... with guest Linh, CTO"` → GUEST_NAME=Linh, GUEST_ROLE=CTO
- `"... episode 12"` → EPISODE_N=12
- `"... English only"` → set `language: en` in episode.json, skip Vietnamese translation

---

## QUALITY CHECKLIST

**Script must have (both EN and VI versions):**
- [ ] Opening with immediate impact — no pleasantries
- [ ] ≥ 50 spoken lines ([HOST] + [GUEST] combined)
- [ ] Spoken word target consistent with language-specific pacing heuristics
- [ ] If `language=vi` and target is 30 min: spoken words >= 5,400 (recommended 5,600+)
- [ ] Pilot-audio projection completed and >= target * 1.08 safety margin
- [ ] If deep-dive, script generated in multiple passes to hit target without truncation
- [ ] Mixed turn lengths: 1-sentence reactions + 3-4 sentence explanations
- [ ] ≥ 2 genuine HOST <-> GUEST disagreements with pushback
- [ ] ≥ 6 data points traceable to research (with numbers)
- [ ] Guest asking questions back to HOST (not one-directional)
- [ ] 3 closing questions with no easy answers

**Script must NOT have:**
- [ ] "Hello everyone", "Welcome to", or any opening pleasantry
- [ ] ≥ 5 consecutive turns by the same speaker
- [ ] All turns the same length (monotonous pacing)
- [ ] "Thanks for listening" / "See you next time" sign-off
- [ ] Markdown formatting (bold, headings, tables) in spoken lines
- [ ] Dashes (em-dash, en-dash) in spoken lines — TTS reads them aloud

**Vietnamese script additional checks:**
- [ ] Natural spoken Vietnamese, not literal word-for-word translation
- [ ] Technical terms adapted per [VIETNAMESE_NOTES.md](references/VIETNAMESE_NOTES.md)
- [ ] Currency/percentage written in spoken form
- [ ] No hyphenated compounds in dialogue

**Audio must produce:**
- [ ] Distinct voices for HOST vs GUEST
- [ ] Intro and outro from fixed assets
- [ ] Transition between segments from fixed assets
- [ ] Valid MP3 with title/artist metadata
- [ ] Duration: 25–35 min (standard) / 40–50 min (deep-dive)

---

## HOOKS (add to `.claude/settings.json`)

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "WebSearch",
      "hooks": [{
        "type": "command",
        "command": "python3 -c \"import json,sys,re; r=json.loads(sys.stdin.read()); t=str(r.get('output','')); has_num=bool(re.search(r'\\d+[%$MBK]?',t)); print('RESEARCH_OK') if has_num else print('RESEARCH_WARN: no concrete numbers — refine query')\""
      }]
    }],
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "python3 -c \"import os,json,glob,datetime; files=glob.glob('./podcast_studio/*/exports/*.mp3',recursive=True); [open(os.path.expanduser('~/.claude/podcast_log.jsonl'),'a').write(json.dumps({'ts':datetime.datetime.now().isoformat(),'file':f})+chr(10)) for f in files] if files else None\""
      }]
    }]
  }
}
```
