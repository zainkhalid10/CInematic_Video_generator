"""phase2_audio/__init__.py — Phase 2 entry point."""

from __future__ import annotations
import time

from phase1_story.serializer import load_script, load_characters
from phase2_audio.manifest_builder import build_timing_manifest
from shared.schema import TimingManifest


def run(run_id: str, ws_callback=None) -> TimingManifest:
    """Run the full Phase 2 audio pipeline."""
    t0 = time.perf_counter()
    print(f"[Phase2] start run_id={run_id}")
    scenes = load_script()
    characters = load_characters()
    manifest = build_timing_manifest(run_id, scenes, characters, ws_callback=ws_callback)
    print(f"[Phase2] done in {time.perf_counter() - t0:.1f}s")
    return manifest
