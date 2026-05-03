"""
phase1_story/__init__.py
========================
Phase 1 pipeline entry point using LangGraph StateGraph.
"""

from __future__ import annotations
import time

from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Any

from phase1_story.story_agent import run_story_agent
from phase1_story.character_agent import run_character_agent
from phase1_story.script_agent import run_script_agent
from phase1_story.serializer import write_story, write_characters, write_script
from phase1_story.tools import build_run_id, validate_story_arc
from shared.schema import StoryOutput


class Phase1State(TypedDict):
    prompt: str
    run_id: str
    arc: Any
    characters: List[Any]
    scenes: List[Any]


def _serialize_node(state: Phase1State) -> Phase1State:
    write_story(state["run_id"], state["arc"])
    write_characters(state["run_id"], state["characters"])
    write_script(state["run_id"], state["scenes"])
    return state


def build_graph() -> Any:
    graph = StateGraph(Phase1State)
    graph.add_node("story_agent", run_story_agent)
    graph.add_node("character_agent", run_character_agent)
    graph.add_node("script_agent", run_script_agent)
    graph.add_node("serialize", _serialize_node)

    graph.set_entry_point("story_agent")
    graph.add_edge("story_agent", "character_agent")
    graph.add_edge("character_agent", "script_agent")
    graph.add_edge("script_agent", "serialize")
    graph.add_edge("serialize", END)
    return graph.compile()


def run(prompt: str, run_id: str | None = None) -> StoryOutput:
    """Run the full Phase 1 pipeline and return a StoryOutput."""
    rid = run_id or build_run_id(prompt)
    t0 = time.perf_counter()
    print(f"[Phase1] LangGraph start run_id={rid}")
    app = build_graph()
    final = app.invoke(
        {"prompt": prompt, "run_id": rid, "arc": None, "characters": [], "scenes": []},
        config={"configurable": {"thread_id": rid}},
    )
    print(f"[Phase1] LangGraph finished in {time.perf_counter() - t0:.1f}s")
    return StoryOutput(
        run_id=rid,
        prompt=prompt,
        arc=final["arc"],
        characters=final["characters"],
        scenes=final["scenes"],
    )
