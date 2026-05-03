"""
shared/schema.py
================
Pydantic models for ALL JSON objects exchanged between phases.
ALL members must approve any changes to this file before modifying phase code.
"""

from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Phase 1 — Story & Script
# ---------------------------------------------------------------------------

class Character(BaseModel):
    id: str = Field(..., description="Unique character identifier, e.g. 'char_1'")
    name: str
    role: Literal["protagonist", "antagonist", "supporting", "narrator"]
    description: str = Field(..., description="Physical appearance and personality")
    voice_id: str = Field(..., description="Coqui TTS speaker ID, e.g. 'p225'")
    mood_default: str = Field(default="neutral", description="Default emotional tone")

    @field_validator("id", mode="before")
    @classmethod
    def coerce_char_id(cls, v):
        if isinstance(v, int):
            return f"char_{v}"
        if isinstance(v, str) and v.strip().isdigit():
            return f"char_{int(v.strip())}"
        return str(v) if v is not None else v


class StoryArc(BaseModel):
    title: str
    genre: str
    theme: str
    logline: str = Field(..., description="One-sentence story summary")
    act_structure: List[str] = Field(
        ..., description="Three-act structure: [setup, confrontation, resolution]"
    )
    total_duration_seconds: float = Field(..., ge=60, le=300)


class DialogueLine(BaseModel):
    character_id: str
    text: str
    emotion: Optional[str] = "neutral"
    pause_after_ms: int = Field(default=300, ge=0)

    @field_validator("character_id", mode="before")
    @classmethod
    def coerce_character_id(cls, v):
        """LLMs often emit 1 instead of \"char_1\"."""
        if isinstance(v, int):
            return f"char_{v}"
        if isinstance(v, str) and v.strip().isdigit():
            return f"char_{int(v.strip())}"
        return str(v) if v is not None else v


class Scene(BaseModel):
    scene_id: str = Field(..., description="e.g. 'scene_001'")
    title: str
    description: str
    visual_prompt: str = Field(
        ..., description="Detailed image generation prompt for this scene"
    )
    camera_motion: Literal["zoom_in", "zoom_out", "pan_left", "pan_right", "static"]
    mood: str = Field(..., description="e.g. mysterious, joyful, tense")
    duration_seconds: float = Field(..., ge=1, le=300)
    dialogue: List[DialogueLine] = Field(default_factory=list)
    background_music: Optional[str] = Field(
        default=None, description="Mood keyword for BGM selection"
    )

    @field_validator("scene_id", mode="before")
    @classmethod
    def coerce_scene_id(cls, v):
        """LLMs often emit 1 instead of \"scene_001\"."""
        if isinstance(v, int):
            return f"scene_{int(v):03d}"
        if isinstance(v, str):
            s = v.strip()
            if s.isdigit():
                return f"scene_{int(s):03d}"
            return s
        return str(v)

    @field_validator("duration_seconds", mode="before")
    @classmethod
    def clamp_duration(cls, v):
        """Clamp to course spec §5.5: 15–60 seconds per scene."""
        v = float(v)
        return max(15.0, min(v, 60.0))


class StoryOutput(BaseModel):
    """Output of Phase 1 story agent — written to outputs/story.json"""
    run_id: str
    prompt: str
    arc: StoryArc
    characters: List[Character]
    scenes: List[Scene]


# ---------------------------------------------------------------------------
# Phase 2 — Audio / Timing Manifest
# ---------------------------------------------------------------------------

class AudioEntry(BaseModel):
    character_id: str
    text: str
    audio_file: str = Field(..., description="Relative path to .wav file")
    start_ms: int
    end_ms: int
    duration_ms: int


class BGMEntry(BaseModel):
    scene_id: str
    audio_file: str
    mood: str
    volume: float = Field(default=0.3, ge=0.0, le=1.0)


class SceneTimingBlock(BaseModel):
    scene_id: str
    start_ms: int
    end_ms: int
    dialogue_entries: List[AudioEntry]
    bgm: Optional[BGMEntry] = None


class TimingManifest(BaseModel):
    """Output of Phase 2 — written to outputs/timing_manifest.json"""
    run_id: str
    scenes: List[SceneTimingBlock]
    total_duration_ms: int


# ---------------------------------------------------------------------------
# Phase 3 — Video Handoff
# ---------------------------------------------------------------------------

class SceneVideoAsset(BaseModel):
    scene_id: str
    image_file: str = Field(..., description="Path to generated image")
    animation_effect: str
    duration_seconds: float


class VideoHandoff(BaseModel):
    """Output of Phase 3 — written to outputs/phase3_video_handoff.json"""
    run_id: str
    output_video: str = Field(default="outputs/final_output.mp4")
    scenes: List[SceneVideoAsset]
    fps: int = 24
    resolution: str = "768x432"


# ---------------------------------------------------------------------------
# Phase 5 — Edit & Intent
# ---------------------------------------------------------------------------

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
    ]
    target: str = Field(..., description="Scene ID, character ID, or 'all'")
    parameters: dict = Field(default_factory=dict)
    confidence: float = Field(..., ge=0.0, le=1.0)


class EditResponse(BaseModel):
    intent: EditIntent
    version: int
    changes_made: List[str]
    message: str
