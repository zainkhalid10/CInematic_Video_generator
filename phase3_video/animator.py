"""
phase3_video/animator.py
=========================
Ken Burns (zoom/pan) animation effects via MoviePy v2.
"""

from __future__ import annotations
import numpy as np
from moviepy import ImageClip, VideoClip


def _zoom_in(clip: ImageClip, duration: float) -> VideoClip:
    """Slowly zoom in from 1.0x to 1.2x scale (spec §7.2)."""
    def make_frame(t):
        scale = 1.0 + 0.2 * (t / duration)
        frame = clip.get_frame(0)
        h, w = frame.shape[:2]
        new_w, new_h = int(w * scale), int(h * scale)
        from PIL import Image
        img = Image.fromarray(frame).resize((new_w, new_h), Image.LANCZOS)
        # Center crop
        left = (new_w - w) // 2
        top  = (new_h - h) // 2
        return np.array(img)[top:top+h, left:left+w]
    return VideoClip(make_frame, duration=duration)


def _zoom_out(clip: ImageClip, duration: float) -> VideoClip:
    """Slowly zoom out from 1.2x to 1.0x scale (spec §7.2)."""
    def make_frame(t):
        scale = 1.2 - 0.2 * (t / duration)
        frame = clip.get_frame(0)
        h, w = frame.shape[:2]
        new_w, new_h = int(w * scale), int(h * scale)
        from PIL import Image
        img = Image.fromarray(frame).resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - w) // 2
        top  = (new_h - h) // 2
        return np.array(img)[top:top+h, left:left+w]
    return VideoClip(make_frame, duration=duration)


def _pan_left(clip: ImageClip, duration: float) -> VideoClip:
    """Pan from right to left across the image."""
    def make_frame(t):
        frame = clip.get_frame(0)
        h, w = frame.shape[:2]
        margin = int(w * 0.1)
        offset = int(margin * (t / duration))
        return frame[:, offset:offset + w - margin] if w > margin else frame
    return VideoClip(make_frame, duration=duration)


def _pan_right(clip: ImageClip, duration: float) -> VideoClip:
    """Pan from left to right across the image."""
    def make_frame(t):
        frame = clip.get_frame(0)
        h, w = frame.shape[:2]
        margin = int(w * 0.1)
        offset = int(margin * (1 - t / duration))
        return frame[:, offset:offset + w - margin] if w > margin else frame
    return VideoClip(make_frame, duration=duration)


def _static(clip: ImageClip, duration: float) -> VideoClip:
    return clip.with_duration(duration)


EFFECT_MAP = {
    "zoom_in":   _zoom_in,
    "zoom_out":  _zoom_out,
    "pan_left":  _pan_left,
    "pan_right": _pan_right,
    "static":    _static,
}


def apply_animation(image_path: str, camera_motion: str, duration: float) -> VideoClip:
    """Return an animated VideoClip from a still image."""
    clip = ImageClip(image_path)
    fn = EFFECT_MAP.get(camera_motion, _static)
    animated = fn(clip, duration)
    animated = animated.with_fps(24)
    return animated
