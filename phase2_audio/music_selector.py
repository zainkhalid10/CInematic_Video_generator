"""
phase2_audio/music_selector.py
================================
Selects background music per scene mood.
Strategy A: MusicGen (GPU/slow)
Strategy B: CC0 royalty-free .mp3 from /assets/bgm/ (instant)
"""

from __future__ import annotations
import time
from pathlib import Path

from shared.constants import BGM_ENGINE, BGM_DIR, OUTPUT_DIR

# Moods supported by the CC0 library strategy
SUPPORTED_MOODS = ["mysterious", "joyful", "tense", "melancholic", "triumphant", "neutral"]


def _closest_mood(mood: str) -> str:
    mood_lower = mood.lower()
    for m in SUPPORTED_MOODS:
        if m in mood_lower or mood_lower in m:
            return m
    return "neutral"


# ---------------------------------------------------------------------------
# Strategy B — CC0 Library (default, instant)
# ---------------------------------------------------------------------------

def _select_from_library(mood: str) -> str:
    target = _closest_mood(mood)
    path = Path(BGM_DIR) / f"{target}.mp3"
    if path.exists():
        return str(path)
    # Fallback to ambient
    neutral = Path(BGM_DIR) / "ambient.mp3"
    if neutral.exists():
        return str(neutral)
    raise FileNotFoundError(
        f"No BGM file found for mood '{mood}'. "
        f"Download CC0 tracks to {BGM_DIR}/ named by mood (e.g. mysterious.mp3)."
    )


# ---------------------------------------------------------------------------
# Strategy A — MusicGen
# ---------------------------------------------------------------------------

def _generate_musicgen(mood: str, duration: float = 20.0) -> str:
    from transformers import pipeline
    from pydub import AudioSegment
    import scipy.io.wavfile as wav
    import numpy as np

    out_path = Path(OUTPUT_DIR) / "audio" / f"bgm_{mood}.wav"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    synth = pipeline("text-to-audio", model="facebook/musicgen-small")
    prompt = f"calm ambient background music for a {mood} animated scene"
    result = synth(prompt, forward_params={"do_sample": True})

    audio_array = result["audio"][0].T  # shape: (channels, samples)
    sr = result["sampling_rate"]
    wav.write(str(out_path), sr, (audio_array * 32767).astype(np.int16))

    # Loop if needed
    segment = AudioSegment.from_wav(str(out_path))
    while len(segment) / 1000 < duration:
        segment = segment + segment
    segment[: int(duration * 1000)].export(str(out_path), format="wav")
    return str(out_path)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def select_bgm(mood: str, duration: float = 20.0) -> str:
    """Return path to BGM audio file for the given mood."""
    engine = BGM_ENGINE.lower()
    if engine == "musicgen":
        return _generate_musicgen(mood, duration)
    return _select_from_library(mood)
