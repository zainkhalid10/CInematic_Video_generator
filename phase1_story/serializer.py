"""
phase1_story/serializer.py
===========================
Writes Phase 1 outputs (story.json, characters.json, script.json) to disk.
"""

from __future__ import annotations
import json
from pathlib import Path

from shared.schema import StoryArc, Character, Scene
from shared.constants import OUTPUT_DIR


def write_story(run_id: str, arc: StoryArc) -> str:
    path = Path(OUTPUT_DIR) / "story.json"
    data = {"run_id": run_id, **arc.model_dump()}
    path.write_text(json.dumps(data, indent=2))
    print(f"[Phase1] story.json written → {path}")
    return str(path)


def write_characters(run_id: str, characters: list[Character]) -> str:
    path = Path(OUTPUT_DIR) / "characters.json"
    data = {"run_id": run_id, "characters": [c.model_dump() for c in characters]}
    path.write_text(json.dumps(data, indent=2))
    print(f"[Phase1] characters.json written → {path}")
    return str(path)


def write_script(run_id: str, scenes: list[Scene]) -> str:
    path = Path(OUTPUT_DIR) / "script.json"
    data = {"run_id": run_id, "scenes": [s.model_dump() for s in scenes]}
    path.write_text(json.dumps(data, indent=2))
    print(f"[Phase1] script.json written → {path}")
    return str(path)


def load_script(path: str = None) -> list[Scene]:
    p = Path(path or f"{OUTPUT_DIR}/script.json")
    raw = json.loads(p.read_text())
    return [Scene(**s) for s in raw["scenes"]]


def load_characters(path: str = None) -> list[Character]:
    p = Path(path or f"{OUTPUT_DIR}/characters.json")
    raw = json.loads(p.read_text())
    return [Character(**c) for c in raw["characters"]]
