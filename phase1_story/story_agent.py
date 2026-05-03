"""
phase1_story/story_agent.py
============================
LangGraph node: generates the story arc from a user prompt.
"""

from __future__ import annotations
import time

from langchain_core.messages import HumanMessage, SystemMessage

from shared.schema import StoryArc
from shared.llm_factory import get_chat_llm_with_fallback
from shared.llm_json import invoke_json_model
from phase1_story.prompts import STORY_AGENT_SYSTEM, STORY_AGENT_USER


def run_story_agent(state: dict) -> dict:
    """LangGraph node — generates StoryArc from prompt."""
    prompt: str = state["prompt"]
    llm = get_chat_llm_with_fallback()
    messages = [
        SystemMessage(content=STORY_AGENT_SYSTEM),
        HumanMessage(content=STORY_AGENT_USER.format(prompt=prompt)),
    ]
    t0 = time.perf_counter()
    arc = invoke_json_model(llm, messages, StoryArc, step_name="story_agent")
    print(f"[Phase1] story_agent total {time.perf_counter() - t0:.1f}s")
    return {**state, "arc": arc}
