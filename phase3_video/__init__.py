"""phase3_video/__init__.py — Phase 3 entry point."""

from __future__ import annotations
import time

from phase1_story.serializer import load_script
from phase2_audio.manifest_builder import load_timing_manifest
from phase3_video.image_generator import generate_all_images
from phase3_video.compositor import composite_video
from shared.schema import VideoHandoff


def run(run_id: str, ws_callback=None) -> VideoHandoff:
    """Run the full Phase 3 pipeline."""
    t0 = time.perf_counter()
    print(f"[Phase3] start run_id={run_id}")
    scenes = load_script()
    manifest = load_timing_manifest()
    image_paths = generate_all_images(scenes, ws_callback=ws_callback)
    handoff = composite_video(scenes, image_paths, manifest, ws_callback=ws_callback)
    print(f"[Phase3] done in {time.perf_counter() - t0:.1f}s")
    return handoff
