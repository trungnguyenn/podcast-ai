# Tech Radar — Audio Production Guide

Reference for audio markers, fixed assets, and the production pipeline.

---

## SCRIPT MARKERS REFERENCE

The parser in `scripts/produce_audio.py` recognises these markers:

### Speech Markers
```
[HOST] spoken text here
[GUEST] spoken text here
```
Each line generates one TTS audio file. Tone cues inside the text (`[laugh]`/`[cuoi nhe]`,
`[pause]`/`[dung lai]`, `[serious]`/`[nghiem tuc]`) are stripped before sending to TTS.

### Music Markers
```
[INTRO_MUSIC]
[OUTRO_MUSIC]
```
Resolved from fixed MP3 assets in the skill `assets/` directory: `intro.mp3` and `outro.mp3`.
No generation required. The renderer reads these shared assets in place from the skill folder.

### Transition Markers
```
[SEGMENT_BREAK: Title of this segment]
[SOUND_EFFECT: label]
```
Both markers resolve to the fixed `assets/transition.mp3`. For `[SEGMENT_BREAK: ...]`, the
audio pipeline can also auto-generate a **HOST spoken section intro** after the transition,
using the segment title. This is enabled by default because it helps listeners re-orient in
long-form episodes.

Example:
```
[SEGMENT_BREAK: Segment 3 — Fatal SMB Mistakes]
```

Will produce:
1. `transition.mp3`
2. HOST TTS line using the configured announcement template.

The spoken title strips prefixes like `Segment 3 —` or `Closing —` before rendering.
The announcement template is language-aware — configure in `voice_config.json`.

### Tone Cues (stripped, no audio output)

English markers:
```
[laugh]        light laughter — strip, no audio
[pause]        thoughtful pause — strip, no audio
[serious]      serious shift — strip, no audio
[energetic]    energetic — strip, no audio
[reflective]   reflective — strip, no audio
```

Vietnamese markers (used in `script_vi.txt`):
```
[cuoi nhe]     light laughter — strip, no audio
[dung lai]     thoughtful pause — strip, no audio
[nghiem tuc]   serious shift — strip, no audio
[nang dong]    energetic — strip, no audio
[khe gat dau]  reflective — strip, no audio
```

---

## FIXED AUDIO ASSETS

All non-speech audio is sourced from pre-recorded files in `assets/`:

| File | Marker | Usage |
|------|--------|-------|
| `assets/intro.mp3` | `[INTRO_MUSIC]` | Played once at episode start |
| `assets/outro.mp3` | `[OUTRO_MUSIC]` | Played once at episode end |
| `assets/transition.mp3` | `[SEGMENT_BREAK:]`, `[SOUND_EFFECT:]` | Played between segments |

To replace any asset, overwrite the file in `assets/` — the next episode run will pick up
the new version automatically.

---

## PRODUCTION PIPELINE

The `scripts/produce_audio.py` script runs these steps in order:

```
1. Load config (voice_config.json + env var overrides)
2. Determine language from episode.json (default: vi)
3. Resolve script file: script_vi.txt (vi) or script_en.txt (en), fallback script.md
4. Resolve provider (`auto`: EN → `edge_tts`/fallback `macos_say`, VI → `vieneu`)
5. Parse script → ordered list of segments
6. Create workspace cache/report dirs: cache/segments/, logs/, exports/
7. Resolve intro/outro/transition from shared skill assets in place
9. Auto-insert HOST section-title announcements after `[SEGMENT_BREAK: ...]` when enabled
10. Apply TTS polish pass to make risky written-tech phrasing more speakable (VI scripts)
11. Generate TTS for each speech segment via selected provider (cached per segment)
12. For VieNeu in `standard` mode, retry a segment in `turbo` when it fails or is too slow (configurable)
13. Merge all in script order with adaptive pauses and optional loudness normalization
14. Write manifest.json
15. Write qa_report.json
16. (Optional) Write benchmark_report.json when `--benchmark` is used
```

**Caching:** Speech segments are cached under `cache/segments/`. Re-runs skip already-generated speech.
- Delete `cache/segments/` to regenerate speech.
- Shared intro/outro/transition assets are not copied into the workspace.

---

## VOICE SETTINGS GUIDE

ElevenLabs settings are configured in `assets/voice_config.json` under `elevenlabs.voice_settings`.

| Setting | Range | Effect |
|---------|-------|--------|
| `stability` | 0–1 | Higher = more consistent, less expressive. 0.4–0.6 works well |
| `similarity_boost` | 0–1 | Higher = closer to original voice sample. 0.7–0.8 recommended |
| `style` | 0–1 | Higher = more stylized/exaggerated delivery. 0.3–0.5 for natural |
| `use_speaker_boost` | bool | Improves voice clarity. Always `true` |

**Recommended presets:**
- Host (authoritative, clear): stability=0.50, similarity=0.75, style=0.35
- Guest analytical: stability=0.55, similarity=0.75, style=0.25
- Guest energetic: stability=0.40, similarity=0.75, style=0.50
- Guest expert: stability=0.55, similarity=0.80, style=0.30

For VieNeu, tune generation under `vieneu.default_request`, voice presets in `vieneu.profiles`,
and pace presets in `vieneu.pace_profiles`. `produce_audio.py` merges them in this order:
default request, speaker profile, pace profile, segment override.

Engine strategy is configured under `vieneu.engine.mode`:
- `standard` for highest quality (default)
- `turbo` for fastest local generation
- `turbo_gpu` for turbo GPU backend
- `auto` to pick draft/final mode from episode intent (`render_purpose`, `purpose`, `mode`, `stage`, `intent`)

For English without paid APIs, use `tts_provider: auto` (default) or `edge_tts` directly.
`auto` picks `edge_tts` when available and falls back to `macos_say`.

| VieNeu Setting | Typical Range | Effect |
|---------|-------|--------|
| `render_mode` | `auto`, `full`, `stream` | `auto` prefers full render when chunk joining matters |
| `max_chars` | 180–260 | Smaller chunks feel snappier; larger chunks preserve context |
| `silence_p` | 0.10–0.18 | Pause inserted when VieNeu joins internal chunks |
| `crossfade_p` | 0.03–0.06 | Smooths chunk joins for long turns |
| `temperature` | 0.76–0.92 | Lower is steadier; higher is livelier |
| `top_k` | 34–54 | Lower is safer; higher adds variation |
| `skip_normalize` | bool | Leave false unless text is already normalized upstream |
| `phonetic_normalize` | bool | Server-side acronym mapping; usually false if script already normalized |

## TTS POLISH

`tts_polish` in `voice_config.json` lets the renderer rewrite risky written-tech phrasing into
more speakable Vietnamese before phonetic normalization.

Typical uses:
- `monthly downloads` → `lượt tải mỗi tháng`
- `2.5 tỷ USD` → `2.5 tỷ đô la Mỹ`
- `workflow coherence` → `độ liền mạch của luồng công việc`
- `tool poisoning` → `đầu độc công cụ`

---

## AUDIO MERGE SETTINGS

Configured in `assets/voice_config.json` under `audio`:

| Setting | Default | Description |
|---------|---------|-------------|
| `gap_turn_ms` | 400 | Silence between speaker turns |
| `gap_segment_ms` | 1200 | Silence before/after segment markers |
| `gap_music_ms` | 2000 | Silence around music blocks |
| `gap_sfx_ms` | 800 | Silence after transition effects |
| `playback_speed` | `1.2` | Speech-only speed multiplier applied per HOST/GUEST segment with `ffmpeg atempo` (pitch-preserving). Music/SFX are not speed-shifted. |
| `playback_speed_by_language.vi` | `1.2` | Default speech speed for Vietnamese episodes |
| `playback_speed_by_language.en` | `1.0` | Default speech speed for English episodes |

Additional section-title settings:

| Setting | Default | Description |
|---------|---------|-------------|
| `segment_title_announcement.enabled` | `true` | Auto-speak a HOST title after `[SEGMENT_BREAK: ...]` |
| `segment_title_announcement.speaker` | `HOST` | Which speaker voice announces the section title |
| `segment_title_announcement.tts_profile` | `host_transition` | VieNeu tuning profile used for generated section announcements |
| `segment_title_announcement.template` | `{"vi": "Bây giờ, chúng ta chuyển sang {title}.", "en": "Now, let's move on to {title}."}` | Spoken template for section intros (per-language dict or plain string) |
| `segment_title_announcement.closing_template` | `{"vi": "Trước khi khép lại, chúng ta đến với {title}.", "en": "Before we wrap up, let's get to {title}."}` | Spoken template for closing sections (per-language dict or plain string) |

Adaptive pause tuning lives under `audio.pause_rules`. Loudness normalization lives under
`audio.loudness_normalization`. Playback speed policy lives under `audio.playback_speed` and
`audio.playback_speed_by_language`.

For duration planning, use speed-adjusted estimates:
`estimated_minutes = spoken_words / (base_wpm * playback_speed_for_language)`.

**Final output:** MP3 with ID3 tags plus `qa_report.json` containing duration, loudness,
silence stats, and remaining risky terms.

---

## TTS PROVIDER SELECTION

Two providers are supported. Select via env var or config:

```bash
# Default: local VieNeu-TTS server
TTS_PROVIDER=vieneu python produce_audio.py --workspace ./podcast_studio/ep[N]_[slug]

# ElevenLabs cloud (requires API key)
TTS_PROVIDER=elevenlabs ELEVENLABS_API_KEY=sk-... python produce_audio.py --workspace ./podcast_studio/ep[N]_[slug]
```

Or set `"tts_provider": "elevenlabs"` in `voice_config.json` to make it the permanent default.

### VieNeu-TTS (local)

| Env var | Default | Description |
|---------|---------|-------------|
| `VIENEU_URL` | `http://127.0.0.1:8001` | Local server URL |
| `VIENEU_ENGINE_MODE` | From `voice_config.json` | Override engine mode: `standard`, `turbo`, `turbo_gpu`, `auto` |
| `HOST_VOICE_ID` | — | Override host voice ID |
| `GUEST_VOICE_ID` | — | Override guest voice ID |
| `GUEST_VOICE_PROFILE` | — | Override guest profile name |

Server can be auto-started by the script. Voice IDs are set in `voice_config.json` under `host.vieneu_voice_id` and `guest_voices[*].vieneu_voice_id`.

Fallback policy is controlled by `vieneu.fallback_standard_to_turbo`:
- `enabled`: allow fallback
- `retry_on_slow`: retry successful but slow segments
- `slow_segment_seconds`: threshold for slow retry

Retry request shaping for turbo fallback is under `vieneu.turbo_retry_request`.

### ElevenLabs (cloud)

| Env var | Required | Description |
|---------|----------|-------------|
| `ELEVENLABS_API_KEY` | Yes | API key from elevenlabs.io |
| `TTS_PROVIDER` | Yes | Set to `elevenlabs` |

Voice IDs must be set in `voice_config.json` under `host.elevenlabs_voice_id` and `guest_voices[*].elevenlabs_voice_id`. Use `eleven_multilingual_v2` model for Vietnamese — configured in the `elevenlabs` section of `voice_config.json`.

To find your ElevenLabs voice IDs: go to elevenlabs.io → Voices → copy the Voice ID for each voice.

## VOICE CLONING FIELDS

Per-speaker cloning references can be provided in either flat or nested form:

```json
{
  "guests": [
    {
      "name": "Dr. Linh",
      "voice_clone": {
        "ref_audio": "/abs/path/linh_ref.wav",
        "ref_text": "Đây là câu tham chiếu.",
        "ref_codes": [1, 2, 3]
      }
    }
  ]
}
```

Equivalent flat keys are also supported on host/guest/profile:
- `ref_audio`
- `ref_text`
- `ref_codes`

Priority order is segment override → guest/host → voice profile.

## BENCHMARK MODE

Run:

```bash
python produce_audio.py --workspace ./podcast_studio/ep[N]_[slug] --benchmark
```

This writes `benchmark_report.json` with:
- Per-segment attempts and latency
- Fallback attempts (`standard` -> `turbo`)
- Total TTS runtime
- Approximate generated-audio duration
- Estimated RTF (`runtime / audio_duration`)

---

## TROUBLESHOOTING

**Rate limit (429) & Timeouts:** Script automatically retries with exponential backoff. For
VieNeu, ensure the local server is running. For ElevenLabs, check your account quota.

**Asset not found:** Ensure `intro.mp3`, `outro.mp3`, and `transition.mp3` are present in
`.agents/skills/tech-radar-podcast/assets/`. The script searches up the directory tree from
the episode folder to locate them.

**VieNeu — Voice not found:** Ensure the requested `voice_id` exists in your VieNeu-TTS
configuration. Run `curl -s http://127.0.0.1:8001/voices` to list available voices.

**ElevenLabs — Voice not found:** Verify `elevenlabs_voice_id` in `voice_config.json` matches
an actual voice ID in your ElevenLabs account. Voice IDs are UUIDs like `pNInz6obpgDQGcFmaJgB`.
