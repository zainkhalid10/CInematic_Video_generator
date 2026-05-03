"""
phase1_story/script_agent.py
=============================
LangGraph node: writes the scene-by-scene script.
"""

from __future__ import annotations
import json
from typing import List

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from shared.schema import Scene
from shared.llm_factory import get_chat_llm_with_fallback
from phase1_story.prompts import SCRIPT_AGENT_SYSTEM, SCRIPT_AGENT_USER


def _get_llm():
    return get_chat_llm_with_fallback()


class ScenesOutput(BaseModel):
    scenes: List[Scene]


def run_script_agent(state: dict) -> dict:
    """LangGraph node — writes scenes from arc + characters."""
    arc = state["arc"]
    characters = state["characters"]

    llm = _get_llm().with_structured_output(ScenesOutput)
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

    # Retry up to 3 times — LLMs sometimes produce values outside schema bounds
    last_error = None
    for attempt in range(3):
        try:
            result: ScenesOutput = llm.invoke(messages)
            # Enforce unique scene_ids (small LLMs often leave this blank)
            for i, scene in enumerate(result.scenes):
                scene.scene_id = f"scene_{i+1:03d}"
            return {**state, "scenes": result.scenes}
        except Exception as e:
            last_error = e
            print(f"[Phase1] Script agent attempt {attempt + 1}/3 failed: {e}")
    raise last_error
