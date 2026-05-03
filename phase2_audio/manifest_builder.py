"""
phase2_audio/manifest_builder.py
==================================
Builds timing_manifest.json by synthesizing all dialogue and measuring durations.
"""

from __future__ import annotations
import json
from pathlib import Path

from pydub import AudioSegment

from shared.schema import (
    Scene, Character, TimingManifest, SceneTimingBlock, AudioEntry, BGMEntry
)
from shared.constants import OUTPUT_DIR
from phase2_audio.tts_engine import synthesize_line
from phase2_audio.music_selector import select_bgm


def _measure_ms(audio_path: str) -> int:
    """Return duration of audio file in milliseconds."""
    return len(AudioSegment.from_file(audio_path))


def build_timing_manifest(
    run_id: str,
    scenes: list[Scene],
    characters: list[Character],
    ws_callback=None,
) -> TimingManifest:
    """
    Synthesize all dialogue, measure durations, assemble TimingManifest.
    ws_callback(event_dict) is called for WebSocket progress updates.
    """
    char_map = {c.id: c for c in characters}
    scene_blocks: list[SceneTimingBlock] = []
    global_start_ms = 0
    total_scenes = len(scenes)

    for scene_idx, scene in enumerate(scenes):
        scene_start_ms = global_start_ms
        scene_audio_entries: list[AudioEntry] = []
        cursor_ms = 0

        for line_idx, line in enumerate(scene.dialogue):
            char = char_map.get(line.character_id)
            if not char:
                continue

            if not line.text or not line.text.strip():
                cursor_ms += line.pause_after_ms
                continue

            audio_filename = f"{scene.scene_id}_line{line_idx:02d}_{line.character_id}.wav"
            audio_path = str(Path(OUTPUT_DIR) / "audio" / audio_filename)

            synthesize_line(
                text=line.text,
                character_role=char.role,
                voice_id=char.voice_id,
                output_path=audio_path,
                emotion=line.emotion or "neutral",
            )

            duration_ms = _measure_ms(audio_path)
            entry = AudioEntry(
                character_id=line.character_id,
                text=line.text,
                audio_file=audio_path,
                start_ms=scene_start_ms + cursor_ms,
                end_ms=scene_start_ms + cursor_ms + duration_ms,
                duration_ms=duration_ms,
            )
            scene_audio_entries.append(entry)
            cursor_ms += duration_ms + line.pause_after_ms

        # Background music
        bgm_entry: BGMEntry | None = None
        mood_key = scene.background_music or scene.mood
        try:
            bgm_path = select_bgm(mood_key, duration=scene.duration_seconds)
            bgm_entry = BGMEntry(
                scene_id=scene.scene_id,
                audio_file=bgm_path,
                mood=mood_key,
            )
        except FileNotFoundError as e:
            print(f"[Phase2] BGM skipped for {scene.scene_id}: {e}")

        scene_end_ms = scene_start_ms + int(scene.duration_seconds * 1000)
        scene_blocks.append(
            SceneTimingBlock(
                scene_id=scene.scene_id,
                start_ms=scene_start_ms,
                end_ms=scene_end_ms,
                dialogue_entries=scene_audio_entries,
                bgm=bgm_entry,
            )
        )

        global_start_ms = scene_end_ms

        if ws_callback:
            ws_callback({
                "phase": 2,
                "node": "manifest_builder",
                "status": "running",
                "message": f"Audio synthesized for scene {scene_idx + 1}/{total_scenes}",
                "progress": (scene_idx + 1) / total_scenes,
            })

    manifest = TimingManifest(
        run_id=run_id,
        scenes=scene_blocks,
        total_duration_ms=global_start_ms,
    )

    # Write to disk
    out_path = Path(OUTPUT_DIR) / "timing_manifest.json"
    out_path.write_text(manifest.model_dump_json(indent=2))
    print(f"[Phase2] timing_manifest.json written → {out_path}")
    return manifest


def load_timing_manifest(path: str | None = None) -> TimingManifest:
    p = Path(path or f"{OUTPUT_DIR}/timing_manifest.json")
    return TimingManifest.model_validate_json(p.read_text())
