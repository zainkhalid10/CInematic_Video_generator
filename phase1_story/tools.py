"""
phase1_story/tools.py
=====================
LangGraph tool functions used by Phase 1 agents.
"""

from __future__ import annotations
import json
import re
from typing import Any

from shared.schema import Scene, StoryArc


def validate_story_arc(arc: StoryArc) -> list[str]:
    """Return a list of validation errors, empty if valid."""
    errors: list[str] = []
    if len(arc.act_structure) != 3:
        errors.append("act_structure must have exactly 3 entries.")
    if arc.total_duration_seconds < 60 or arc.total_duration_seconds > 300:
        errors.append("total_duration_seconds must be between 60 and 300.")
    return errors


def estimate_duration(scenes: list[Scene]) -> float:
    """Return total duration in seconds across all scenes."""
    return sum(s.duration_seconds for s in scenes)


def sanitize_llm_json(raw: str) -> Any:
    """Strip markdown fences and parse JSON from LLM output."""
    # Remove ```json ... ``` or ``` ... ```
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().strip("`").strip()
    return json.loads(cleaned)


def build_run_id(prompt: str) -> str:
    """Generate a short deterministic run ID from a prompt."""
    import hashlib, time
    digest = hashlib.md5(f"{prompt}{time.time()}".encode()).hexdigest()[:8]
    return f"run_{digest}"
