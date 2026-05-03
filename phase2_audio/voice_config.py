"""
phase2_audio/voice_config.py
=============================
Maps character roles to Coqui VITS speakers (spec §6.2) and edge-tts voices (optional engine).
"""

from __future__ import annotations

import re

from phase2_audio.music_selector import _closest_mood

# Spec §6.2 — Coqui VCTK VITS speaker IDs
ROLE_TO_COQUI_SPEAKER: dict[str, str] = {
    "protagonist": "p225",
    "antagonist": "p245",
    "supporting": "p256",
    "narrator": "p376",
}

# Role → edge-tts voice (when TTS_ENGINE=edge-tts)
ROLE_TO_EDGE_VOICE: dict[str, str] = {
    "protagonist": "en-US-GuyNeural",
    "antagonist": "en-US-EricNeural",
    "supporting": "en-US-JennyNeural",
    "narrator": "en-US-AriaNeural",
}

_COQUI_SPEAKER_RE = re.compile(r"^p\d{3}$")


def get_speaker(character_role: str, voice_id: str | None = None) -> str:
    """Return Coqui VITS speaker id (spec table); honor explicit p### from character."""
    if voice_id and _COQUI_SPEAKER_RE.match(voice_id):
        return voice_id
    return ROLE_TO_COQUI_SPEAKER.get(character_role, "p225")


def get_edge_voice(character_role: str, voice_id: str | None = None) -> str:
    """Return edge-tts voice name; allow full voice string from character."""
    if voice_id and voice_id.startswith("en-"):
        return voice_id
    return ROLE_TO_EDGE_VOICE.get(character_role, "en-US-GuyNeural")


# Bark presets (spec §6.3) — map role to history_prompt
ROLE_TO_BARK_PRESET: dict[str, str] = {
    "protagonist": "v2/en_speaker_6",
    "antagonist": "v2/en_speaker_8",
    "supporting": "v2/en_speaker_3",
    "narrator": "v2/en_speaker_9",
}


def get_bark_preset(character_role: str) -> str:
    return ROLE_TO_BARK_PRESET.get(character_role, "v2/en_speaker_6")


def apply_emotion_tag(text: str, emotion: str) -> str:
    """Lightweight cues for Bark-style prosody; harmless for Coqui/edge."""
    em = (emotion or "neutral").lower().strip()
    prefixes = {
        "sad": "[sighs] ",
        "angry": "[angry] ",
        "fearful": "[gasps] ",
        "happy": "[laughs] ",
        "surprised": "[gasps] ",
        "whisper": "[whispers] ",
        "neutral": "",
    }
    prefix = prefixes.get(em, "")
    return f"{prefix}{text}" if prefix else text
