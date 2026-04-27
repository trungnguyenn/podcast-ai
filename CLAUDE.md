# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PodcastAI is an autonomous podcast production platform that generates Vietnamese tech podcasts. It combines Claude API (research, scripting) with edge-tts (text-to-speech) and ffmpeg/pydub (audio assembly) to produce broadcast-quality episodes with minimal manual intervention.

Three podcast skills are available:
- **tech-radar-podcast** — Full-featured episodes (25-50 min) with host + guest(s)
- **daily-ai-podcast** — Solo-host daily AI news briefing (~20 min)
- **weekly-ai-podcast** — Two-host weekly recap with dialogue (~40-45 min)

## Editorial principle for `daily-ai-podcast` and `weekly-ai-podcast`

Both skills are built around a single **"Who we're making this for"** section inside their `SKILL.md`. That section is the source of truth for audience — software builders, managers, and consultants who move across legacy upkeep, modernization, feature enhancement, greenfield builds, and AI-agent proposals, with roughly half working in healthcare software. Every phase file (`references/PHASES.md`) and script guide (`references/SCRIPT_GUIDE.md`) points back to it rather than restating.

When working on these two skills, **do not add fixed segments, quotas, checklists, scoring rules, or schema fields to enforce healthcare, legacy/greenfield, or short/mid/long-horizon framing.** The audience understanding is deliberately carried by prose — research, curation, and scripting are expected to re-read the audience section and let its specificity guide their choices. Force-fitting a healthcare reference or legacy-modernization callout when the story doesn't support it is worse than leaving it out. If content quality isn't landing, update the audience section first; only add structure if prose alone demonstrably fails.

This principle applies to `daily-ai-podcast` and `weekly-ai-podcast` only. `tech-radar-podcast` is a different format and unaffected.

## H3Tech hiro-crew Context

H3Tech and Trung are developing **hiro-crew**, an internal agentic software-delivery control plane. When podcast work touches agentic software delivery, multi-agent engineering workflows, AI coding governance, runtime harnesses, MCP/tool safety, delivery evidence, gates, receipts, or control-plane patterns, treat hiro-crew as an important internal reference point.

Primary hiro-crew references:
- BRD: `/Users/trungnguyen/Working/H3Tech/hiro-crew/docs/brd/brd-all.md`
- v3.0 spec: `/Users/trungnguyen/Working/H3Tech/hiro-crew/docs/v3.0/v3-spec.md`

Current hiro-crew product frame:
- hiro-crew is H3Tech's internal agentic software-delivery control plane, built first around Claude Code.
- The product combines a delivery control plane with an agent runtime harness.
- The durable control-plane layer owns project identity, specs, task graph, policy, gates, evidence, receipts, audit, cost telemetry, domain packs, and dashboards.
- The runtime harness executes agents against those contracts. Claude Code is the v3.0 harness; future versions should support additional runtime adapters.
- v3.0 shifts the product from "agents run work" to "agents produce governed, spec-driven, evidence-backed delivery."

For any **tech-radar-podcast** episode related to agentic software-delivery control planes, AI coding governance, MCP/tool integration safety, autonomous delivery workflows, or production-grade agent operations:

1. Read the hiro-crew BRD and v3.0 spec before finalizing the outline.
2. Add a short editorial lens that connects the topic back to hiro-crew: what the episode implies for specs, gates, policy, tool profiles, evidence, receipts, audit, runtime adapters, or dashboard workflows.
3. Identify any hiro-crew coverage gaps revealed by the episode topic. Examples include destructive-tool approval, production blast-radius control, scoped agent identities, backup/recovery evidence, MCP trust boundaries, runtime-level tool enforcement, or incident-response evidence.
4. Suggest concrete enhancements for `/Users/trungnguyen/Working/H3Tech/hiro-crew/docs/v3.0/v3-spec.md`. Do not edit that external file unless the user explicitly asks for the spec update in the current turn; otherwise, include the proposed v3-spec additions in the episode workspace notes or final delivery summary.
5. Keep the podcast audience-first. The hiro-crew linkage should sharpen the analysis and product feedback; it should not turn the episode into an internal product pitch unless the user asks for that framing.

## Architecture

### TTS Engine

All text-to-speech is handled by **edge-tts** (Microsoft Edge cloud TTS, free, no local server needed). No local TTS server or submodule is required.

### Podcast Production Pipeline (`.agents/skills/`)

All three skills follow a 7-phase autonomous pipeline: **briefing -> research -> outline/curate -> script (EN+VI) -> TTS audio -> merge -> delivery**. No user confirmation between phases.

Key shared components live in `.agents/skills/tech-radar-podcast/`:
- `scripts/produce_audio.py` — Audio orchestrator (TTS synthesis + merge), used by all skills
- `assets/voice_config.json` — Voice profiles, audio gap config
- `assets/intro.mp3`, `outro.mp3`, `transition.mp3` — Fixed audio jingles

Each episode gets an isolated workspace under `podcast_studio/` (e.g., `podcast_studio/daily_0409/`, `podcast_studio/ep05_topic_slug/`) containing scripts, research, audio cache, and final exports.

### TTS Provider Routing

| Language | Provider |
|----------|----------|
| All languages | edge-tts (free, no local server needed) |

### Script Format

Plain text with line-based markers parsed by `produce_audio.py`:
- `[HOST] text` / `[GUEST] text` / `[GUEST_2] text` — TTS-rendered spoken lines
- `[INTRO_MUSIC]` / `[OUTRO_MUSIC]` — Fixed asset insertion
- `[SEGMENT_BREAK: Title]` — Transition audio + optional announcement
- `[laugh]` / `[pause]` — Tone cues, stripped before TTS (no audio)

No markdown formatting in spoken lines. No dashes (TTS reads them aloud).

## Common Commands

### Audio Production

```bash
# Ensure deps
pip install edge-tts pydub audioop-lts
ffmpeg -version  # must be available

# Produce audio for an episode workspace
python3 .agents/skills/tech-radar-podcast/scripts/produce_audio.py \
  --workspace ./podcast_studio/ep01_slug

# With benchmarking
python3 .agents/skills/tech-radar-podcast/scripts/produce_audio.py \
  --workspace ./podcast_studio/ep01_slug --benchmark
```

## Key Configuration

- **Voice & audio tuning**: `.agents/skills/tech-radar-podcast/assets/voice_config.json` — voice profiles, playback speed (default 1.2x for Vietnamese), phonetic normalization rules
- **Series continuity**: `podcast_studio/daily_series_context.json` and `weekly_series_context.json` — track covered stories to avoid duplicates

## Vietnamese Script Conventions

- Vietnamese TTS speaks faster than expected at 1.2x playback; duration formula: `estimated_min = spoken_words / (base_wpm * 1.2)`
- 20-min daily: minimum 3,600 spoken words; 30-min standard: minimum 5,400; 40-45 min weekly: minimum 8,500
- Technical terms adapted per `.agents/skills/*/references/VIETNAMESE_NOTES.md` (e.g., "AI" -> "Ay Ai")
- Currency/percentages written in spoken form; no hyphenated compounds in dialogue
