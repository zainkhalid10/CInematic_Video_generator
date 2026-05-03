"""
phase1_story/character_agent.py
================================
LangGraph node: designs the cast of characters.
"""

from __future__ import annotations
from typing import List

from langchain_core.messages import HumanMessage, SystemMessage

from shared.schema import Character
from shared.llm_factory import get_chat_llm_with_fallback
from phase1_story.prompts import CHARACTER_AGENT_SYSTEM, CHARACTER_AGENT_USER


def _get_llm():
    return get_chat_llm_with_fallback()


def run_character_agent(state: dict) -> dict:
    """LangGraph node — designs characters from the story arc."""
    from pydantic import BaseModel

    class CharactersOutput(BaseModel):
        characters: List[Character]

    arc = state["arc"]
    llm = _get_llm().with_structured_output(CharactersOutput)

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
    result: CharactersOutput = llm.invoke(messages)
    return {**state, "characters": result.characters}
