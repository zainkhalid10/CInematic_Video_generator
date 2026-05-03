"""
phase1_story/script_agent.py
=============================
LangGraph node: writes the scene-by-scene script.
"""

from __future__ import annotations
import json
import time
from typing import List

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, model_validator

from shared.schema import Scene
from shared.llm_factory import get_chat_llm_with_fallback
from shared.llm_json import invoke_json_model
from phase1_story.prompts import SCRIPT_AGENT_SYSTEM, SCRIPT_AGENT_USER


class ScenesOutput(BaseModel):
    scenes: List[Scene]

    @model_validator(mode="before")
    @classmethod
    def normalize_payload(cls, data):
        """Accept raw list, single scene dict, or missing \"scenes\" wrapper."""
        if isinstance(data, list):
            return {"scenes": data}
        if isinstance(data, dict) and "scenes" not in data:
            markers = ("scene_id", "visual_prompt", "camera_motion", "duration_seconds")
            if any(k in data for k in markers):
                return {"scenes": [data]}
        return data


def run_script_agent(state: dict) -> dict:
    """LangGraph node — writes scenes from arc + characters."""
    arc = state["arc"]
    characters = state["characters"]

    llm = get_chat_llm_with_fallback()
    messages = [
        SystemMessage(content=SCRIPT_AGENT_SYSTEM),
        HumanMessage(
            content=SCRIPT_AGENT_USER.format(
                arc_json=arc.model_dump_json(indent=2),
                characters_json=json.dumps(
                    [c.model_dump() for c in characters], indent=2
                ),
            )
        ),
    ]
    t0 = time.perf_counter()
    result = invoke_json_model(llm, messages, ScenesOutput, step_name="script_agent", max_retries=3)
    for i, scene in enumerate(result.scenes):
        scene.scene_id = f"scene_{i+1:03d}"
    print(f"[Phase1] script_agent total {time.perf_counter() - t0:.1f}s")
    return {**state, "scenes": result.scenes}
