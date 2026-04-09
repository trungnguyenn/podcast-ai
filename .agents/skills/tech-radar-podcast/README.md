# tech-radar-podcast

A Claude Code skill that autonomously produces full Vietnamese tech podcast episodes from a single topic prompt. Runs 100% locally — no external API costs.

**Podcast:** *Tech Radar* — a Vietnamese tech podcast with a permanent host (Trung) and one guest expert per episode.

---

## Invoke

```
/tech-radar-podcast "Tạo podcast về autonomous AI agents trong healthcare US"
/tech-radar-podcast "Làm episode về tương lai của Claude AI và Devin"
/tech-radar-podcast "Kubernetes adoption in Southeast Asia"
```

Inline overrides:
```
"... deep-dive"              → 45–50 min episode (≥ 80 spoken lines)
"... với guest là Linh, CTO" → override guest name and role
"... tập 12"                 → set episode number
```

Duration heuristic:
- Slow: 100–120 words/minute
- Medium: 130–160 words/minute
- Fast: 170–200+ words/minute
- Default Tech Radar target: medium-fast Vietnamese delivery

---

## What it does

The skill runs a 7-phase pipeline autonomously — no confirmation prompts between phases:

| Phase | Output | What happens |
|-------|--------|-------------|
| 1 Briefing | `request.json`, `episode.json`, `status.json` | Parse topic, preserve the original request, create episode workspace |
| 2 Research | `research/research.json`, `research/raw/` | Persist merged research plus raw research artifacts |
| 3 Outline | `outline.md` | 5-segment structure, duration target based on pacing bands |
| 4 Script | `script_en.txt`, `script_vi.txt`, `prompts/` | Dialogue plus prompt history |
| 5 Audio Production | `cache/segments/`, `exports/` | TTS speech into workspace cache while shared runtime/assets stay in the skill |
| 6 Merge | `exports/[slug]_final.mp3` | Stitch everything in script order, add ID3 tags |
| 7 Tracking | `workspace_manifest.json`, `status.json`, `logs/` | Persistent workspace state and reports |

**Episode workspace:**
```
podcast_studio/ep[N]_[slug]/
├── request.json
├── episode.json
├── status.json
├── workspace_manifest.json
├── research/
│   ├── research.json
│   └── raw/
├── prompts/
├── logs/
├── cache/
│   └── segments/
├── outline.md
├── script_en.txt
├── script_vi.txt
├── manifest.json
├── qa_report.json
└── exports/
    └── [slug]_[lang]_final.mp3
```

---

## Skill structure

```
.agents/skills/tech-radar-podcast/
├── SKILL.md                    # Skill entry point (Claude reads this first)
├── README.md                   # This file
├── assets/
│   ├── voice_config.json       # Voice profiles, VieNeu URL, audio gap settings
│   ├── intro.mp3               # Fixed intro — used for [INTRO_MUSIC]
│   ├── outro.mp3               # Fixed outro — used for [OUTRO_MUSIC]
│   └── transition.mp3          # Fixed transition — used for [SEGMENT_BREAK:]
├── references/
│   ├── PHASES.md               # Detailed per-phase production instructions
│   ├── SCRIPT_GUIDE.md         # Dialogue rules, HOST/GUEST personas, tone cues
│   └── AUDIO_GUIDE.md          # Audio pipeline, voice settings, troubleshooting
└── scripts/
    ├── init_episode.py         # Workspace bootstrapper
    ├── produce_audio.py        # Audio orchestration script (shared, run in place)
    └── vieneu_hq_server.py     # VieNeu-TTS 0.5B FastAPI server (Apple Silicon)
```

---

## Setup

### 1. Start the VieNeu-TTS server

```bash
/path/to/venv/bin/python \
    .agents/skills/tech-radar-podcast/scripts/vieneu_hq_server.py
```

Listens on `http://127.0.0.1:8001`. Verify: `curl http://127.0.0.1:8001/health`

### 2. Initialize an episode workspace

```bash
python3 .agents/skills/tech-radar-podcast/scripts/init_episode.py \
  --request "Create a podcast about autonomous AI agents in healthcare US" \
  --topic "Autonomous AI agents in healthcare US" \
  --episode 18
```

### 3. Install Python dependencies

```bash
python3 -c "import requests, pydub; print('deps: OK')" 2>/dev/null \
  || pip install requests pydub audioop-lts --quiet
ffmpeg -version | head -1 || echo "WARNING: brew install ffmpeg"
```

---

## Configuration

Edit `assets/voice_config.json` to change:
- `vieneu.url` — TTS server URL (default: `http://127.0.0.1:8001`)
- `host.vieneu_voice_id` — Host voice (Trung, fixed)
- `guest_voices` — Guest voice profiles and their topic keywords
- `audio` — Gap timings between turns, segments, and music

See [references/AUDIO_GUIDE.md](references/AUDIO_GUIDE.md) for full documentation.

Shared skill resources are no longer copied into each episode workspace. The renderer reads shared code and fixed audio from the skill folder, and writes only episode-owned artifacts into `podcast_studio/...`.

### Script markers

| Marker | Audio |
|--------|-------|
| `[HOST] text` | TTS — host voice |
| `[GUEST] text` | TTS — auto-selected guest voice |
| `[INTRO_MUSIC]` | `assets/intro.mp3` |
| `[OUTRO_MUSIC]` | `assets/outro.mp3` |
| `[SEGMENT_BREAK: title]` | `assets/transition.mp3` |
| `[cuoi nhe]` / `[dung lai]` / `[nghiem tuc]` | Tone cues — stripped, no audio |

### Guest voice auto-selection

The guest voice is chosen automatically from `voice_config.json` by matching the episode topic against `best_for_topics` in each profile:

| Topic area | Profile |
|-----------|---------|
| AI/ML, cloud, security, data | `male_analytical` or `female_researcher` |
| Developer tools, startups, product | `male_energetic` |
| Healthcare, compliance, legal, executive | `female_expert` |

Override with `GUEST_VOICE_PROFILE=male_analytical` env var, or inline: `"... với guest là Linh, CTO"`.
