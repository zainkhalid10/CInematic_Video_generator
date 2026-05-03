"""
phase1_story/tests/test_phase1.py
==================================
Unit tests for Phase 1 story pipeline.
"""

import json
import pytest
from unittest.mock import MagicMock, patch

from shared.schema import StoryArc, Character, Scene, DialogueLine
from phase1_story.tools import validate_story_arc, estimate_duration, sanitize_llm_json, build_run_id
from phase1_story.serializer import write_story, write_characters, write_script, load_script, load_characters


# --- Fixtures ---

@pytest.fixture
def sample_arc():
    return StoryArc(
        title="The Lost Signal",
        genre="sci-fi",
        theme="hope",
        logline="A lone astronaut discovers a mysterious signal that could save humanity.",
        act_structure=["Astronaut receives faint signal", "Signal leads to danger", "Humanity is saved"],
        total_duration_seconds=90.0,
    )


@pytest.fixture
def sample_characters():
    return [
        Character(id="char_1", name="Alex", role="protagonist",
                  description="Brave young astronaut", voice_id="p225", mood_default="determined"),
        Character(id="char_2", name="Nova", role="supporting",
                  description="AI companion aboard the ship", voice_id="p240", mood_default="calm"),
    ]


@pytest.fixture
def sample_scenes():
    return [
        Scene(
            scene_id="scene_001",
            title="The Signal",
            description="Alex detects a signal from deep space",
            visual_prompt="Cinematic astronaut at a glowing control panel, space visible through porthole",
            camera_motion="zoom_in",
            mood="mysterious",
            duration_seconds=30.0,
            dialogue=[DialogueLine(character_id="char_1", text="What is that?", emotion="surprised")],
        ),
        Scene(
            scene_id="scene_002",
            title="The Journey",
            description="The ship races toward the source",
            visual_prompt="Spaceship flying through a colorful nebula at high speed, dramatic lighting",
            camera_motion="pan_right",
            mood="tense",
            duration_seconds=40.0,
            dialogue=[],
        ),
    ]


# --- Tool Tests ---

def test_validate_story_arc_valid(sample_arc):
    errors = validate_story_arc(sample_arc)
    assert errors == []


def test_validate_story_arc_bad_acts(sample_arc):
    sample_arc.act_structure = ["only one act"]
    errors = validate_story_arc(sample_arc)
    assert any("act_structure" in e for e in errors)


def test_validate_story_arc_bad_duration(sample_arc):
    sample_arc.total_duration_seconds = 500
    errors = validate_story_arc(sample_arc)
    assert any("total_duration_seconds" in e for e in errors)


def test_estimate_duration(sample_scenes):
    total = estimate_duration(sample_scenes)
    assert total == 70.0


def test_sanitize_llm_json():
    raw = '```json\n{"key": "value"}\n```'
    result = sanitize_llm_json(raw)
    assert result == {"key": "value"}


def test_build_run_id():
    rid = build_run_id("test prompt")
    assert rid.startswith("run_")
    assert len(rid) == 12  # run_ + 8 hex chars


# --- Serializer Tests ---

def test_write_and_load_script(tmp_path, monkeypatch, sample_scenes):
    monkeypatch.setattr("phase1_story.serializer.OUTPUT_DIR", str(tmp_path))
    write_script("run_test", sample_scenes)
    loaded = load_script(str(tmp_path / "script.json"))
    assert len(loaded) == 2
    assert loaded[0].scene_id == "scene_001"


def test_write_and_load_characters(tmp_path, monkeypatch, sample_characters):
    monkeypatch.setattr("phase1_story.serializer.OUTPUT_DIR", str(tmp_path))
    write_characters("run_test", sample_characters)
    loaded = load_characters(str(tmp_path / "characters.json"))
    assert len(loaded) == 2
    assert loaded[0].name == "Alex"
