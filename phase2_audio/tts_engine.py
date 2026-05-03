"""
phase2_audio/tts_engine.py
===========================
TTS per course spec §6: Coqui (primary), Bark (alt), edge-tts (optional, no heavy deps).
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from shared.constants import OUTPUT_DIR, TTS_ENGINE, COQUI_MODEL
from phase2_audio.voice_config import (
    get_speaker,
    get_edge_voice,
    get_bark_preset,
    apply_emotion_tag,
)

logger = logging.getLogger(__name__)

_coqui_tts = None


def _get_coqui():
    global _coqui_tts
    if _coqui_tts is None:
        try:
            from TTS.api import TTS
        except ImportError as e:
            raise RuntimeError(
                "Coqui TTS is not installed or unsupported on this Python version. "
                "The upstream `TTS` package requires Python <3.12. Options: "
                "(1) set TTS_ENGINE=edge-tts in .env, or "
                "(2) use a Python 3.11 virtualenv and pip install TTS."
            ) from e

        logger.info("Loading Coqui TTS model %s (first run may download ~200MB)...", COQUI_MODEL)
        _coqui_tts = TTS(COQUI_MODEL)
    return _coqui_tts


def _synthesize_coqui(text: str, speaker: str, output_path: str) -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    tts = _get_coqui()
    tts.tts_to_file(text=text, file_path=output_path, speaker=speaker)
    return output_path


def _synthesize_bark(text: str, character_role: str, output_path: str) -> str:
    try:
        import numpy as np
        from bark import SAMPLE_RATE, generate_audio
        import soundfile as sf
    except ImportError as e:
        raise RuntimeError(
            "Bark TTS requires optional deps: pip install suno-bark soundfile. "
            "Or set TTS_ENGINE=coqui or edge-tts."
        ) from e

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    preset = get_bark_preset(character_role)
    audio = generate_audio(text, history_prompt=preset)
    sf.write(output_path, audio, SAMPLE_RATE)
    return output_path


async def _synthesize_edge_async(text: str, voice: str, output_path: str) -> str:
    """edge-tts emits MP3; we re-encode as WAV so MoviePy/ffmpeg read duration + codec reliably."""
    import edge_tts
    from pydub import AudioSegment

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_mp3 = out_path.with_name(out_path.stem + "_tts.mp3")
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(tmp_mp3))
    seg = AudioSegment.from_file(str(tmp_mp3))
    seg.export(str(out_path), format="wav")
    tmp_mp3.unlink(missing_ok=True)
    return str(out_path)


def synthesize_line(
    text: str,
    character_role: str,
    voice_id: str,
    output_path: str,
    emotion: str = "neutral",
) -> str:
    """Synthesize one dialogue line; engine from TTS_ENGINE env."""
    tagged = apply_emotion_tag(text, emotion)
    engine = (TTS_ENGINE or "coqui").lower()

    if engine in ("edge", "edge-tts"):
        voice = get_edge_voice(character_role, voice_id)
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(
                        asyncio.run,
                        _synthesize_edge_async(tagged, voice, output_path),
                    )
                    return future.result()
            return loop.run_until_complete(_synthesize_edge_async(tagged, voice, output_path))
        except RuntimeError:
            return asyncio.run(_synthesize_edge_async(tagged, voice, output_path))

    if engine == "bark":
        return _synthesize_bark(tagged, character_role, output_path)

    if engine == "coqui":
        speaker = get_speaker(character_role, voice_id)
        return _synthesize_coqui(tagged, speaker, output_path)

    raise ValueError(f"Unknown TTS_ENGINE={engine!r}; use coqui | bark | edge-tts")
