"""
phase5_edit/intent_schema.py
==============================
Pydantic model for the LangGraph intent classification output.
"""

from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field


class EditIntent(BaseModel):
    action: Literal[
        "change_scene_mood",
        "rewrite_dialogue",
        "change_visual_style",
        "apply_filter",
        "change_bgm",
        "adjust_pacing",
        "regenerate_image",
        "change_voice",
        "add_subtitle",
        "revert_version",
    ] = Field(..., description="The type of edit action to perform")
    target: str = Field(
        ..., description="Scene ID (e.g. 'scene_001'), character ID, or 'all'"
    )
    parameters: dict = Field(
        default_factory=dict,
        description="Action-specific parameters, e.g. {'mood': 'joyful'} or {'filter': 'grayscale'}",
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence 0–1")
