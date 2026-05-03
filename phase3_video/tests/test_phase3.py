"""
phase3_video/tests/test_phase3.py
===================================
Unit tests for Phase 3 video pipeline.
"""

import pytest
from unittest.mock import patch, MagicMock
from phase3_video.animator import EFFECT_MAP
from phase3_video.image_generator import NEGATIVE_PROMPT


def test_all_camera_motions_covered():
    required = {"zoom_in", "zoom_out", "pan_left", "pan_right", "static"}
    assert required.issubset(set(EFFECT_MAP.keys()))


def test_negative_prompt_contains_quality_terms():
    assert "blurry" in NEGATIVE_PROMPT
    assert "watermark" in NEGATIVE_PROMPT


@patch("phase3_video.image_generator.asyncio.run")
@patch("phase3_video.image_generator.IMAGE_ENGINE", "pollinations")
def test_generate_image_pollinations_calls_async(mock_run, tmp_path, monkeypatch):
    monkeypatch.setattr("phase3_video.image_generator.OUTPUT_DIR", str(tmp_path))
    mock_run.return_value = str(tmp_path / "images" / "scene_001.png")
    import time
    with patch("phase3_video.image_generator.time.sleep"):
        from phase3_video.image_generator import generate_image
        result = generate_image("A bright city scene", "scene_001")
    mock_run.assert_called_once()


@patch("phase3_video.image_generator.requests.post")
@patch("phase3_video.image_generator.IMAGE_ENGINE", "automatic1111")
def test_generate_image_a1111(mock_post, tmp_path, monkeypatch):
    import base64
    from PIL import Image
    import io

    monkeypatch.setattr("phase3_video.image_generator.OUTPUT_DIR", str(tmp_path))
    (tmp_path / "images").mkdir()

    # Create a fake 1x1 PNG
    buf = io.BytesIO()
    Image.new("RGB", (1, 1)).save(buf, format="PNG")
    fake_b64 = base64.b64encode(buf.getvalue()).decode()
    mock_post.return_value.json.return_value = {"images": [fake_b64]}
    mock_post.return_value.raise_for_status = MagicMock()

    from phase3_video.image_generator import generate_image
    result = generate_image("test prompt", "scene_001")
    assert result.endswith("scene_001.png")
