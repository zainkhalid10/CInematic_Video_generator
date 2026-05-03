"""
phase1_story/character_agent.py
================================
LangGraph node: designs the cast of characters.
"""

from __future__ import annotations
import time
from typing import List

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from shared.schema import Character
from shared.llm_factory import get_chat_llm_with_fallback
from shared.llm_json import invoke_json_model
from phase1_story.prompts import CHARACTER_AGENT_SYSTEM, CHARACTER_AGENT_USER


class CharactersOutput(BaseModel):
    characters: List[Character]


def run_character_agent(state: dict) -> dict:
    """LangGraph node — designs characters from the story arc."""
    arc = state["arc"]
    llm = get_chat_llm_with_fallback()
    messages = [
        SystemMessage(content=CHARACTER_AGENT_SYSTEM),
        HumanMessage(
            content=CHARACTER_AGENT_USER.format(
                title=arc.title,
                logline=arc.logline,
                genre=arc.genre,
            )
        ),
    ]
    t0 = time.perf_counter()
    result = invoke_json_model(llm, messages, CharactersOutput, step_name="character_agent")
    print(f"[Phase1] character_agent total {time.perf_counter() - t0:.1f}s")
    return {**state, "characters": result.characters}
