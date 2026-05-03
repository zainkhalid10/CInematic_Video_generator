"""
phase5_edit/executor.py
========================
Routes EditIntent to the correct phase re-runner or filter application.
"""

from __future__ import annotations
import json
from pathlib import Path

from shared.constants import OUTPUT_DIR
from phase5_edit.intent_schema import EditIntent
from phase5_edit.filters import apply_filter


def execute_intent(intent: EditIntent, run_id: str) -> list[str]:
    """
    Execute an edit intent and return a list of human-readable change descriptions.
    """
    action = intent.action
    target = intent.target
    params = intent.parameters
    changes: list[str] = []

    if action == "apply_filter":
        filter_name = params.get("filter", "grayscale")
        image_dir = Path(OUTPUT_DIR) / "images"
        targets = (
            list(image_dir.glob("*.png"))
            if target == "all"
            else [image_dir / f"{target}.png"]
        )
        for img_path in targets:
            if img_path.exists():
                apply_filter(str(img_path), filter_name, str(img_path))
                changes.append(f"Applied '{filter_name}' filter to {img_path.name}")

    elif action == "change_scene_mood":
        new_mood = params.get("mood", "neutral")
        _patch_script_field(target, "mood", new_mood)
        changes.append(f"Changed mood of {target} to '{new_mood}'")

    elif action == "rewrite_dialogue":
        new_text = params.get("text", "")
        line_idx = int(params.get("line_index", 0))
        _patch_dialogue_line(target, line_idx, new_text)
        changes.append(f"Rewrote dialogue line {line_idx} in {target}")
        # Re-run Phase 2 for this scene only (simplified: re-run all)
        import phase2_audio as p2
        p2.run(run_id)
        changes.append("Re-synthesized audio after dialogue change")

    elif action == "regenerate_image":
        _regenerate_scene_image(target)
        changes.append(f"Regenerated image for {target}")

    elif action == "change_bgm":
        new_mood = params.get("mood", "neutral")
        _patch_script_field(target, "background_music", new_mood)
        changes.append(f"Changed BGM mood for {target} to '{new_mood}'")

    elif action == "adjust_pacing":
        delta = float(params.get("delta_seconds", 5.0))
        _patch_script_field(target, "duration_seconds_delta", delta)
        changes.append(f"Adjusted pacing of {target} by {delta:+.1f}s")

    elif action == "change_visual_style":
        new_style = params.get("style", "cinematic")
        _patch_script_field(target, "visual_style", new_style)
        changes.append(f"Changed visual style of {target} to '{new_style}'")

    elif action == "add_subtitle":
        from phase3_video.subtitle_overlay import burn_subtitles
        from phase2_audio.manifest_builder import load_timing_manifest
        manifest = load_timing_manifest()
        video = str(Path(OUTPUT_DIR) / "final_output.mp4")
        out_sub = str(Path(OUTPUT_DIR) / "final_output_sub.mp4")
        burn_subtitles(video, manifest, out_sub)
        changes.append("Burned subtitles onto video")

    elif action == "revert_version":
        version = int(params.get("version", 1))
        changes.append(f"Triggered revert to version {version} (handled by StateManager)")

    else:
        changes.append(f"Unknown action '{action}' — no operation performed")

    return changes


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_script() -> list[dict]:
    p = Path(OUTPUT_DIR) / "script.json"
    return json.loads(p.read_text())["scenes"]


def _save_script(run_id: str, scenes: list[dict]):
    p = Path(OUTPUT_DIR) / "script.json"
    p.write_text(json.dumps({"run_id": run_id, "scenes": scenes}, indent=2))


def _patch_script_field(scene_id: str, field: str, value):
    p = Path(OUTPUT_DIR) / "script.json"
    data = json.loads(p.read_text())
    for scene in data["scenes"]:
        if scene_id == "all" or scene["scene_id"] == scene_id:
            scene[field] = value
    p.write_text(json.dumps(data, indent=2))


def _patch_dialogue_line(scene_id: str, line_idx: int, new_text: str):
    p = Path(OUTPUT_DIR) / "script.json"
    data = json.loads(p.read_text())
    for scene in data["scenes"]:
        if scene["scene_id"] == scene_id:
            if line_idx < len(scene.get("dialogue", [])):
                scene["dialogue"][line_idx]["text"] = new_text
    p.write_text(json.dumps(data, indent=2))


def _regenerate_scene_image(scene_id: str):
    from phase3_video.image_generator import generate_image
    p = Path(OUTPUT_DIR) / "script.json"
    data = json.loads(p.read_text())
    for scene in data["scenes"]:
        if scene["scene_id"] == scene_id:
            generate_image(scene["visual_prompt"], scene_id)
            return
    raise ValueError(f"Scene '{scene_id}' not found in script.json")
