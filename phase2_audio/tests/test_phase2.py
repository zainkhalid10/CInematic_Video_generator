"""
phase2_audio/tests/test_phase2.py
===================================
Unit tests for Phase 2 audio pipeline.
"""

import pytest
from unittest.mock import patch, MagicMock
from phase2_audio.voice_config import get_speaker, apply_emotion_tag, _closest_mood
from phase2_audio.music_selector import _closest_mood as music_closest_mood, SUPPORTED_MOODS


def test_get_speaker_by_role():
    assert get_speaker("protagonist") == "p225"
    assert get_speaker("antagonist") == "p245"


def test_get_speaker_prefers_voice_id():
    assert get_speaker("protagonist", voice_id="p300") == "p300"


def test_apply_emotion_tag_sad():
    result = apply_emotion_tag("I lost everything.", "sad")
    assert result.startswith("[sighs]")


def test_apply_emotion_tag_neutral():
    result = apply_emotion_tag("Hello world.", "neutral")
    assert result == "Hello world."


def test_closest_mood_exact():
    assert music_closest_mood("mysterious") == "mysterious"


def test_closest_mood_partial():
    assert music_closest_mood("very mysterious night") == "mysterious"


def test_closest_mood_fallback():
    assert music_closest_mood("unknown_xyz") == "neutral"


def test_supported_moods_complete():
    required = {"mysterious", "joyful", "tense", "melancholic", "triumphant", "neutral"}
    assert required.issubset(set(SUPPORTED_MOODS))


@patch("phase2_audio.manifest_builder.synthesize_line")
@patch("phase2_audio.manifest_builder._measure_ms", return_value=2000)
@patch("phase2_audio.manifest_builder.select_bgm", side_effect=FileNotFoundError("no bgm"))
def test_build_timing_manifest_no_bgm(mock_bgm, mock_measure, mock_synth, tmp_path, monkeypatch):
    monkeypatch.setattr("phase2_audio.manifest_builder.OUTPUT_DIR", str(tmp_path))
    (tmp_path / "audio").mkdir()

    from shared.schema import Scene, Character, DialogueLine
    scenes = [
        Scene(
            scene_id="scene_001", title="T", description="D",
            visual_prompt="P", camera_motion="static", mood="neutral",
            duration_seconds=10.0,
            dialogue=[DialogueLine(character_id="char_1", text="Hello", emotion="neutral")],
        )
    ]
    chars = [Character(id="char_1", name="A", role="protagonist",
                       description="X", voice_id="p225", mood_default="neutral")]

    from phase2_audio.manifest_builder import build_timing_manifest
    manifest = build_timing_manifest("run_test", scenes, chars)

    assert manifest.run_id == "run_test"
    assert len(manifest.scenes) == 1
    assert manifest.scenes[0].bgm is None
