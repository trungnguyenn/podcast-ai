# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PodcastAI is an autonomous podcast production platform that generates Vietnamese tech podcasts. It combines Claude API (research, scripting) with VieNeu-TTS (Vietnamese text-to-speech) and ffmpeg/pydub (audio assembly) to produce broadcast-quality episodes with minimal manual intervention.

Three podcast skills are available:
- **tech-radar-podcast** — Full-featured episodes (25-50 min) with host + guest(s)
- **daily-ai-podcast** — Solo-host daily AI news briefing (~20 min)
- **weekly-ai-podcast** — Two-host weekly recap with dialogue (~40-45 min)

## Architecture

### VieNeu-TTS (git submodule at `VieNeu-TTS/`)

Vietnamese TTS engine (v2.4.3) with a factory pattern for backend selection:

```python
from vieneu import Vieneu
tts = Vieneu(mode="turbo")   # CPU GGUF — fast, lower quality
tts = Vieneu(mode="standard") # PyTorch GPU — high quality
tts = Vieneu(mode="fast")     # LMDeploy GPU — faster PyTorch
tts = Vieneu(mode="remote", api_base="http://localhost:8001")  # API client
```

Core library lives in `VieNeu-TTS/src/vieneu/`. Base class (`base.py`) provides voice management, phoneme caching, codec loading (NeuCodec), and 24kHz audio output. Factory (`factory.py`) selects the backend. Each mode has its own module (`turbo.py`, `standard.py`, `fast.py`, `remote.py`).

### Podcast Production Pipeline (`.agents/skills/`)

All three skills follow a 7-phase autonomous pipeline: **briefing -> research -> outline/curate -> script (EN+VI) -> TTS audio -> merge -> delivery**. No user confirmation between phases.

Key shared components live in `.agents/skills/tech-radar-podcast/`:
- `scripts/produce_audio.py` — Audio orchestrator (TTS synthesis + merge), used by all skills
- `scripts/vieneu_hq_server.py` — FastAPI wrapper around VieNeu for local serving
- `assets/voice_config.json` — Voice profiles, TTS provider routing, audio gap config
- `assets/intro.mp3`, `outro.mp3`, `transition.mp3` — Fixed audio jingles

Each episode gets an isolated workspace under `podcast_studio/` (e.g., `podcast_studio/daily_0409/`, `podcast_studio/ep05_topic_slug/`) containing scripts, research, audio cache, and final exports.

### TTS Provider Routing

| Language | Primary Provider | Fallback |
|----------|-----------------|----------|
| Vietnamese (`vi`) | VieNeu (local server on :8001) | — |
| English (`en`) | edge-tts (free) | macos-say |

Routing is automatic based on `language` field in `episode.json`.

### Script Format

Plain text with line-based markers parsed by `produce_audio.py`:
- `[HOST] text` / `[GUEST] text` / `[GUEST_2] text` — TTS-rendered spoken lines
- `[INTRO_MUSIC]` / `[OUTRO_MUSIC]` — Fixed asset insertion
- `[SEGMENT_BREAK: Title]` — Transition audio + optional announcement
- `[laugh]` / `[pause]` — Tone cues, stripped before TTS (no audio)

No markdown formatting in spoken lines. No dashes (TTS reads them aloud).

## Common Commands

### VieNeu-TTS Setup & Development

```bash
cd VieNeu-TTS
make check              # Verify toolchain (python, uv, espeak, docker, GPU)
make setup              # uv sync (CPU/turbo mode)
uv sync --group gpu     # Include GPU dependencies
uv run vieneu-web       # Gradio UI at http://127.0.0.1:7860
uv run vieneu-stream    # Streaming web UI (CPU GGUF)
uv run pytest tests/    # Run tests
```

### TTS Server for Podcast Production

```bash
# Start VieNeu FastAPI server (required before producing Vietnamese episodes)
python3 .agents/skills/tech-radar-podcast/scripts/vieneu_hq_server.py
# Health check: curl http://127.0.0.1:8001/health

# Server endpoints: GET /voices, POST /stream, POST /set_model, POST /reset, GET /health
```

### Audio Production

```bash
# Ensure deps
pip install requests pydub audioop-lts
ffmpeg -version  # must be available

# Produce audio for an episode workspace
python3 .agents/skills/tech-radar-podcast/scripts/produce_audio.py \
  --workspace ./podcast_studio/ep01_slug

# With benchmarking
python3 .agents/skills/tech-radar-podcast/scripts/produce_audio.py \
  --workspace ./podcast_studio/ep01_slug --benchmark
```

### Docker (GPU)

```bash
cd VieNeu-TTS
make docker-gpu                    # docker compose with GPU profile
make docker-build-serve            # Build serve image
docker run --gpus all -p 23333:23333 pnnbao/vieneu-tts:serve --tunnel
```

## Key Configuration

- **VieNeu-TTS package config**: `VieNeu-TTS/pyproject.toml` — Python >=3.10, uses `uv` package manager
- **Voice & audio tuning**: `.agents/skills/tech-radar-podcast/assets/voice_config.json` — voices, engine mode, pace profiles, playback speed (default 1.2x for Vietnamese), phonetic normalization rules
- **Series continuity**: `podcast_studio/daily_series_context.json` and `weekly_series_context.json` — track covered stories to avoid duplicates

## Vietnamese Script Conventions

- Vietnamese TTS speaks faster than expected at 1.2x playback; duration formula: `estimated_min = spoken_words / (base_wpm * 1.2)`
- 20-min daily: minimum 3,600 spoken words; 30-min standard: minimum 5,400; 40-45 min weekly: minimum 8,500
- Technical terms adapted per `.agents/skills/*/references/VIETNAMESE_NOTES.md` (e.g., "AI" -> "Ay Ai")
- Currency/percentages written in spoken form; no hyphenated compounds in dialogue
