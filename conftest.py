"""conftest.py — Shared pytest fixtures."""
import pytest


@pytest.fixture(autouse=True)
def _patch_output_dir(tmp_path, monkeypatch):
    """Redirect all OUTPUT_DIR usages to a temp directory for isolated tests."""
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path))
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test_state.db"))
    yield
