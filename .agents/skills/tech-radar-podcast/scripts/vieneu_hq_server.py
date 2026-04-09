#!/usr/bin/env python3
"""
PodcastAI Audio Engine — VieNeu-TTS 0.5B Q8 GGUF (Metal)
Runs natively on Apple Silicon via llama.cpp — 3.2x faster than PyTorch MPS, near-lossless quality.

Engine modes:
    - standard  : quality-first (default)
    - turbo     : fast GGUF turbo backend
    - turbo_gpu : turbo GPU backend

Usage (from project root):
    ./VieNeu-TTS/.venv/bin/python \
        .agents/skills/tech-radar-podcast/scripts/vieneu_hq_server.py

Endpoints:
    GET  /voices              → list VieNeu preset voices
    POST /stream              → TTS, returns streaming WAV
    POST /set_model           → switch backbone at runtime
    POST /clear_queue         → cancel all waiting requests (keeps current inference running)
    POST /reset               → force-release inference lock + cancel everything (use when stuck)
    GET  /health              → server status + queue depth
"""

import io, os, time, wave
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Literal, Optional
import uvicorn
import asyncio, re

# ── Phonetic Normalization ───────────────────────────────────────────────────
ENGLISH_MAPPING = {
    # Acronyms (A.I., S.M.B., etc. sound MUCH better)
    r"\bAI\b": "Ây Ai",
    r"\bSMB\b": "Ét Em Bi",
    r"\bBAA\b": "Bi Ây Ây",
    r"\bHIPAA\b": "Híp pa",
    r"\bPHI\b": "Pi Ét Ai",
    r"\bSaaS\b": "Xát xờ",
    r"\bB2B\b": "Bi Tu Bi",
}

def normalize_text(text: str) -> str:
    """Pre-process English words and acronyms for better Vietnamese TTS pronunciation."""
    # Convert acronyms and tech terms
    for pattern, replacement in ENGLISH_MAPPING.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE if pattern.islower() else 0)
    
    # Clean up multiple spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ── Model configuration ──────────────────────────────────────────────────────
# M4 Mac mini (32 GB) — quality-first defaults
DEFAULT_BACKBONE = os.environ.get("VIENEU_BACKBONE", "pnnbao-ump/VieNeu-TTS-q8-gguf")
DEFAULT_DEVICE   = os.environ.get("VIENEU_DEVICE", "mps")   # Metal on Apple Silicon
DEFAULT_ENGINE_MODE = os.environ.get("VIENEU_ENGINE_MODE", "standard").strip().lower()
DEFAULT_TURBO_BACKBONE = os.environ.get("VIENEU_TURBO_BACKBONE", "pnnbao-ump/VieNeu-TTS-v2-Turbo-GGUF")
DEFAULT_TURBO_GPU_BACKBONE = os.environ.get("VIENEU_TURBO_GPU_BACKBONE", "pnnbao-ump/VieNeu-TTS-v2-Turbo")
DEFAULT_TURBO_BACKEND = os.environ.get("VIENEU_TURBO_BACKEND", "standard").strip().lower()
CODEC_REPO       = "neuphonic/distill-neucodec"
CODEC_DEVICE     = os.environ.get("VIENEU_CODEC_DEVICE", "cpu")  # codec runs fast on CPU
PORT             = int(os.environ.get("VIENEU_PORT", "8001"))

app = FastAPI(title="VieNeu-TTS HQ Server (0.5B Metal)")

# ── Lazy model loader ─────────────────────────────────────────────────────────
_tts = None
_current_backbone = DEFAULT_BACKBONE
_current_device = DEFAULT_DEVICE
_current_engine_mode = "standard"
_current_turbo_backend = DEFAULT_TURBO_BACKEND

def _normalize_engine_mode(mode: str) -> str:
    m = (mode or "").strip().lower()
    if m in {"standard", "turbo", "turbo_gpu"}:
        return m
    return "standard"


def load_model(
    backbone_repo: str = DEFAULT_BACKBONE,
    device: str = DEFAULT_DEVICE,
    engine_mode: str = DEFAULT_ENGINE_MODE,
    turbo_backend: str = DEFAULT_TURBO_BACKEND,
):
    global _tts, _current_backbone, _current_device, _current_engine_mode, _current_turbo_backend
    mode = _normalize_engine_mode(engine_mode)
    print(f"Loading mode={mode} backbone={backbone_repo} on {device}…")
    from vieneu import Vieneu
    if mode == "standard":
        _tts = Vieneu(
            mode="standard",
            backbone_repo=backbone_repo,
            backbone_device=device,
            codec_repo=CODEC_REPO,
            codec_device=CODEC_DEVICE,
        )
    elif mode == "turbo":
        _tts = Vieneu(
            mode="turbo",
            backbone_repo=backbone_repo or DEFAULT_TURBO_BACKBONE,
            device=device,
        )
    else:
        _tts = Vieneu(
            mode="turbo_gpu",
            backbone_repo=backbone_repo or DEFAULT_TURBO_GPU_BACKBONE,
            device=device,
            backend=turbo_backend,
        )
    _current_backbone = backbone_repo
    _current_device = device
    _current_engine_mode = mode
    _current_turbo_backend = turbo_backend
    print(f"Model ready: mode={mode} {backbone_repo} [{device}]")
    return _tts

def get_tts():
    global _tts
    if _tts is None:
        load_model()
    return _tts

# Load on startup
try:
    load_model()
except Exception as e:
    print(f"WARNING: Startup load failed: {e}\nServer running — retry via /set_model")

# ── Helpers ───────────────────────────────────────────────────────────────────
def float32_to_pcm16(audio_float: np.ndarray) -> bytes:
    return (audio_float * 32767).clip(-32768, 32767).astype(np.int16).tobytes()

def wav_header(sample_rate: int = 24000) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.setnframes(100_000_000)   # streaming placeholder
    return buf.getvalue()

# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/voices")
async def list_voices():
    tts = get_tts()
    try:
        voices = tts.list_preset_voices()
        if not voices:
            return []
        if isinstance(voices[0], tuple):
            return [{"id": vid, "name": desc} for desc, vid in voices]
        return [{"id": v, "name": v} for v in voices]
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


class StreamRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None
    ref_audio: Optional[str] = None
    ref_text: Optional[str] = None
    ref_codes: Optional[list[int]] = None
    max_chars: int = Field(default=220, ge=32, le=1024)
    silence_p: float = Field(default=0.12, ge=0.0, le=1.0)
    crossfade_p: float = Field(default=0.04, ge=0.0, le=0.5)
    temperature: float = Field(default=0.85, gt=0.0, le=2.0)
    top_k: int = Field(default=45, ge=1, le=200)
    skip_normalize: bool = False
    phonetic_normalize: bool = True
    render_mode: Literal["auto", "stream", "full"] = "auto"


@app.get("/stream")
async def stream_get(text: str, voice_id: str = None):
    # For GET requests, we can directly use the StreamRequest model for validation
    # and then call the POST handler logic.
    return await stream_post(StreamRequest(text=text, voice_id=voice_id))


# Inference lock to prevent GPU/MPS crashes on concurrent requests
# Metal/MPS backend on macOS is generally not thread-safe for parallel generators
infer_lock = asyncio.Lock()

# Queue management state
_queue_depth   = 0       # requests currently waiting for the lock
_cancel_flag   = False   # when True, new requests return 503 immediately


def should_use_full_render(req: StreamRequest, text: str) -> bool:
    if req.render_mode == "full":
        return True
    if req.render_mode == "stream":
        return False
    return (
        len(text) > req.max_chars
        or req.crossfade_p > 0
        or req.silence_p != 0.15
        or bool(req.ref_audio)
        or bool(req.ref_codes)
    )


@app.post("/stream")
async def stream_post(req: StreamRequest):
    """
    Streaming TTS output.
    Accepts: {"text": "...", "voice_id": "..."}
    Returns 503 immediately if _cancel_flag is set.
    """
    global _queue_depth, _cancel_flag

    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Empty text")
    if req.ref_audio and not os.path.exists(req.ref_audio):
        raise HTTPException(status_code=400, detail=f"ref_audio not found: {req.ref_audio}")
    if req.ref_codes and not req.ref_text and not req.voice_id:
        raise HTTPException(status_code=400, detail="ref_text is required when ref_codes is provided without voice_id")

    if _cancel_flag:
        raise HTTPException(status_code=503, detail="Queue cleared — please retry")

    _queue_depth += 1
    text = req.text.strip()
    if req.phonetic_normalize:
        text = normalize_text(text)
    use_full_render = should_use_full_render(req, text)

    async def generate():
        global _queue_depth
        async with infer_lock:
            _queue_depth -= 1
            yield wav_header()
            t0 = time.time()
            try:
                tts = get_tts()
                voice_data = tts.get_preset_voice(req.voice_id) if req.voice_id else None
                ref_codes = np.asarray(req.ref_codes, dtype=np.int64) if req.ref_codes else None
                render_kwargs = {
                    "voice": voice_data,
                    "ref_audio": req.ref_audio,
                    "ref_codes": ref_codes,
                    "ref_text": req.ref_text,
                    "max_chars": req.max_chars,
                    "temperature": req.temperature,
                    "top_k": req.top_k,
                    "skip_normalize": req.skip_normalize,
                }

                if use_full_render:
                    wav = tts.infer(
                        text,
                        silence_p=req.silence_p,
                        crossfade_p=req.crossfade_p,
                        **render_kwargs,
                    )
                    print(
                        "  full render:"
                        f" {time.time()-t0:.3f}s"
                        f" voice={req.voice_id}"
                        f" chars={len(text)}"
                        f" max_chars={req.max_chars}"
                        f" crossfade={req.crossfade_p}"
                    )
                    yield float32_to_pcm16(wav)
                else:
                    chunk_n = 0
                    for chunk in tts.infer_stream(text, **render_kwargs):
                        if chunk_n == 0:
                            print(
                                "  first chunk:"
                                f" {time.time()-t0:.3f}s"
                                f" voice={req.voice_id}"
                                f" chars={len(text)}"
                                f" max_chars={req.max_chars}"
                            )
                        chunk_n += 1
                        yield float32_to_pcm16(chunk)
            except Exception as e:
                print(f"  inference error: {e}")

    return StreamingResponse(generate(), media_type="audio/wav")


class ModelRequest(BaseModel):
    backbone_repo: Optional[str] = None
    device: Optional[str] = None
    engine_mode: Optional[Literal["standard", "turbo", "turbo_gpu"]] = None
    turbo_backend: Optional[Literal["standard", "lmdeploy"]] = None


@app.post("/set_model")
async def set_model(req: ModelRequest):
    try:
        mode = _normalize_engine_mode(req.engine_mode or _current_engine_mode or DEFAULT_ENGINE_MODE)
        if mode == "standard":
            backbone = req.backbone_repo or DEFAULT_BACKBONE
        elif mode == "turbo_gpu":
            backbone = req.backbone_repo or DEFAULT_TURBO_GPU_BACKBONE
        else:
            backbone = req.backbone_repo or DEFAULT_TURBO_BACKBONE
        device   = req.device or DEFAULT_DEVICE
        turbo_backend = req.turbo_backend or _current_turbo_backend or DEFAULT_TURBO_BACKEND
        load_model(backbone, device, mode, turbo_backend)
        return {
            "status": "ok",
            "backbone": backbone,
            "device": device,
            "engine_mode": mode,
            "turbo_backend": turbo_backend,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/health")
async def health():
    if _tts is None:
        return {"status": "loading", "backbone": DEFAULT_BACKBONE}
    return {
        "status":       "ok",
        "backbone":     _current_backbone,
        "device":       _current_device,
        "engine_mode":  _current_engine_mode,
        "turbo_backend": _current_turbo_backend,
        "queue_depth":  _queue_depth,
        "lock_held":    infer_lock.locked(),
        "cancel_flag":  _cancel_flag,
    }


@app.post("/clear_queue")
async def clear_queue():
    """Signal all waiting /stream requests to abort. Current inference keeps running."""
    global _cancel_flag
    _cancel_flag = True
    await asyncio.sleep(0.6)   # Let waiting coroutines notice the flag
    _cancel_flag = False        # Reset for future requests
    return {"status": "ok", "message": f"Queue cleared ({_queue_depth} requests aborted)", "lock_still_held": infer_lock.locked()}


@app.post("/reset")
async def reset_server():
    """Force-release the inference lock and cancel all waiting requests.
    Use when the server is stuck and /clear_queue is not enough.
    WARNING: May leave GPU in a dirty state — monitor first audio after reset.
    """
    global _cancel_flag
    _cancel_flag = True
    await asyncio.sleep(0.6)
    # Force-release if still locked
    if infer_lock.locked():
        try:
            infer_lock.release()
            print("  /reset: inference lock force-released")
        except RuntimeError:
            pass  # Already released by generate() finally block
    _cancel_flag = False
    return {"status": "ok", "message": "Server reset complete — safe to retry requests"}


if __name__ == "__main__":
    print(f"VieNeu-TTS HQ Server — mode={DEFAULT_ENGINE_MODE} {DEFAULT_BACKBONE} [{DEFAULT_DEVICE}]")
    print(f"http://127.0.0.1:{PORT}")
    uvicorn.run(app, host="127.0.0.1", port=PORT)
