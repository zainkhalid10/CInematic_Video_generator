"""
phase5_edit/tests/test_phase5.py
==================================
Unit tests for Phase 5 edit & undo system.
"""

import pytest
import numpy as np
import cv2
from unittest.mock import patch, MagicMock
from phase5_edit.filters import apply_filter, FILTER_MAP
from phase5_edit.intent_schema import EditIntent


# --- Filter Tests ---

@pytest.fixture
def sample_image(tmp_path):
    """Create a small test PNG."""
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    path = str(tmp_path / "test.png")
    cv2.imwrite(path, img)
    return path


def test_all_filters_work(sample_image, tmp_path):
    out = str(tmp_path / "out.png")
    for name in FILTER_MAP:
        result = apply_filter(sample_image, name, out)
        assert result == out, f"Filter '{name}' did not return output path"


def test_unknown_filter_raises(sample_image, tmp_path):
    with pytest.raises(ValueError, match="Unknown filter"):
        apply_filter(sample_image, "nonexistent_filter", str(tmp_path / "out.png"))


def test_missing_image_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        apply_filter(str(tmp_path / "ghost.png"), "grayscale", str(tmp_path / "out.png"))


# --- Intent Schema Tests ---

def test_edit_intent_valid():
    intent = EditIntent(
        action="apply_filter",
        target="scene_001",
        parameters={"filter": "sepia"},
        confidence=0.95,
    )
    assert intent.action == "apply_filter"
    assert intent.confidence == 0.95


def test_edit_intent_invalid_action():
    with pytest.raises(Exception):
        EditIntent(
            action="delete_everything",  # not a valid action
            target="all",
            parameters={},
            confidence=0.9,
        )


def test_edit_intent_confidence_bounds():
    with pytest.raises(Exception):
        EditIntent(
            action="apply_filter",
            target="all",
            parameters={},
            confidence=1.5,  # > 1.0
        )


# --- StateManager Tests ---

def test_state_manager_snapshot_and_revert(tmp_path):
    from shared.state_manager import StateManager
    db = str(tmp_path / "test.db")
    mgr = StateManager(db_path=db)

    # Snapshot v1
    mgr.snapshot(1, "run_abc", {"key": "value1"}, [], summary="Initial")
    # Snapshot v2
    mgr.snapshot(2, "run_abc", {"key": "value2"}, [], summary="Edit 1")

    history = mgr.history()
    assert len(history) == 2
    assert history[0]["version"] == 1

    state = mgr.revert(1)
    assert state["key"] == "value1"


def test_state_manager_revert_missing_version(tmp_path):
    from shared.state_manager import StateManager
    mgr = StateManager(db_path=str(tmp_path / "test.db"))
    with pytest.raises(ValueError, match="not found"):
        mgr.revert(99)


def test_state_manager_latest_version(tmp_path):
    from shared.state_manager import StateManager
    mgr = StateManager(db_path=str(tmp_path / "test.db"))
    assert mgr.latest_version() == 0
    mgr.snapshot(1, "r", {}, [])
    mgr.snapshot(2, "r", {}, [])
    assert mgr.latest_version() == 2
