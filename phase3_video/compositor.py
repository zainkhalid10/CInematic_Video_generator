"""
phase3_video/compositor.py
===========================
Stitches scene clips (image + animation + audio) into final_output.mp4.
"""

from __future__ import annotations
import json
from pathlib import Path

from moviepy import (
    ImageClip, AudioFileClip, CompositeAudioClip,
    concatenate_videoclips, VideoClip,
)

from shared.schema import Scene, SceneTimingBlock, TimingManifest, VideoHandoff, SceneVideoAsset
from shared.constants import (
    OUTPUT_DIR,
    VIDEO_FPS,
    VIDEO_CODEC,
    AUDIO_CODEC,
    BGM_VOLUME,
    VIDEO_CRF,
)
from phase3_video.animator import apply_animation


def _build_scene_audio(block: SceneTimingBlock) -> CompositeAudioClip | None:
    """Layer dialogue audio + BGM for one scene."""
    clips = []

    for entry in block.dialogue_entries:
        if Path(entry.audio_file).exists():
            ac = AudioFileClip(entry.audio_file).with_start(entry.start_ms / 1000 - block.start_ms / 1000)
            clips.append(ac)

    if block.bgm and Path(block.bgm.audio_file).exists():
        scene_duration = (block.end_ms - block.start_ms) / 1000
        bgm_clip = AudioFileClip(block.bgm.audio_file).subclipped(0, scene_duration).with_volume_scaled(BGM_VOLUME)
        clips.append(bgm_clip)

    if not clips:
        return None
    return CompositeAudioClip(clips)


def composite_video(
    scenes: list[Scene],
    image_paths: dict[str, str],
    manifest: TimingManifest,
    output_path: str | None = None,
    ws_callback=None,
) -> VideoHandoff:
    """
    For each scene: load image → animate → attach audio → concatenate.
    Writes final_output.mp4 and returns VideoHandoff.
    """
    out_path = output_path or str(Path(OUTPUT_DIR) / "final_output.mp4")
    block_map = {b.scene_id: b for b in manifest.scenes}
    video_clips = []
    video_assets: list[SceneVideoAsset] = []

    for idx, scene in enumerate(scenes):
        img_path = image_paths.get(scene.scene_id)
        if not img_path or not Path(img_path).exists():
            print(f"[Phase3] Missing image for {scene.scene_id}, skipping.")
            continue

        # Animate
        clip: VideoClip = apply_animation(img_path, scene.camera_motion, scene.duration_seconds)

        # Attach audio
        block = block_map.get(scene.scene_id)
        if block:
            audio = _build_scene_audio(block)
            if audio:
                clip = clip.with_audio(audio)

        video_clips.append(clip)
        video_assets.append(SceneVideoAsset(
            scene_id=scene.scene_id,
            image_file=img_path,
            animation_effect=scene.camera_motion,
            duration_seconds=scene.duration_seconds,
        ))

        if ws_callback:
            ws_callback({
                "phase": 3, "node": "compositor",
                "status": "running",
                "message": f"Composited scene {idx+1}/{len(scenes)}",
                "progress": 0.5 + (idx + 1) / len(scenes) * 0.4,
            })

    if not video_clips:
        raise RuntimeError("No video clips to composite. Check image generation step.")

    # Concatenate all scenes
    final = concatenate_videoclips(video_clips, method="compose")
    ffmpeg_params = ["-crf", str(VIDEO_CRF), "-preset", "medium"]
    final.write_videofile(
        out_path,
        fps=VIDEO_FPS,
        codec=VIDEO_CODEC,
        audio_codec=AUDIO_CODEC,
        ffmpeg_params=ffmpeg_params,
        logger=None,
    )
    print(f"[Phase3] Raw video written → {out_path}")

    try:
        from phase3_video.subtitle_overlay import burn_subtitles
        import shutil
        subbed_path = out_path.replace(".mp4", "_subtitled.mp4")
        burn_subtitles(out_path, manifest, subbed_path)
        shutil.move(subbed_path, out_path)
        print(f"[Phase3] Subtitles burned → {out_path}")
    except Exception as e:
        print(f"[Phase3] Warning: Subtitle burn-in failed: {e}")

    if ws_callback:
        ws_callback({
            "phase": 3, "node": "compositor", "status": "done",
            "message": "Video ready!", "progress": 1.0,
            "video_url": f"/api/download/{Path(out_path).name}",
        })

    handoff = VideoHandoff(run_id=manifest.run_id, output_video=out_path, scenes=video_assets)
    Path(OUTPUT_DIR, "phase3_video_handoff.json").write_text(handoff.model_dump_json(indent=2))
    return handoff
