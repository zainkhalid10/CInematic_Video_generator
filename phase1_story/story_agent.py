"""
phase1_story/story_agent.py
============================
LangGraph node: generates the story arc from a user prompt.
"""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from shared.schema import StoryArc
from shared.llm_factory import get_chat_llm_with_fallback
from phase1_story.prompts import STORY_AGENT_SYSTEM, STORY_AGENT_USER


def _get_llm():
    return get_chat_llm_with_fallback()


def run_story_agent(state: dict) -> dict:
    """LangGraph node — generates StoryArc from prompt."""
    prompt: str = state["prompt"]
    llm = _get_llm().with_structured_output(StoryArc)

    messages = [
        SystemMessage(content=STORY_AGENT_SYSTEM),
        HumanMessage(content=STORY_AGENT_USER.format(prompt=prompt)),
    ]
    arc: StoryArc = llm.invoke(messages)
    return {**state, "arc": arc}