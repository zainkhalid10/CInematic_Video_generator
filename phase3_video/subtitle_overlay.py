"""
phase3_video/subtitle_overlay.py
==================================
Optional subtitle burn-in using MoviePy v2 TextClip.
"""

from __future__ import annotations
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

from shared.schema import TimingManifest


def burn_subtitles(video_path: str, manifest: TimingManifest, output_path: str) -> str:
    """Burn subtitle text onto video at timed positions."""
    clip = VideoFileClip(video_path)
    subtitles = []

    for block in manifest.scenes:
        for entry in block.dialogue_entries:
            txt = TextClip(
                text=entry.text,
                font_size=24,
                color="white",
                stroke_color="black",
                stroke_width=1,
                method="caption",
                size=(int(clip.w * 0.85), None),
            )
            start_s = entry.start_ms / 1000
            end_s   = entry.end_ms / 1000
            txt = txt.with_position(("center", "bottom")).with_start(start_s).with_end(end_s)
            subtitles.append(txt)

    final = CompositeVideoClip([clip, *subtitles])
    final.write_videofile(output_path, fps=clip.fps, logger=None)
    print(f"[Phase3] Subtitled video written → {output_path}")
    return output_path
