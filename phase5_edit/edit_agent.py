"""
phase5_edit/edit_agent.py
==========================
LangGraph StateGraph for intent classification and edit execution.
Includes the 10 required few-shot examples in the system prompt.
"""

from __future__ import annotations
from typing import TypedDict, List, Any

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from shared.llm_factory import get_chat_llm_with_fallback
from phase5_edit.intent_schema import EditIntent
from phase5_edit.executor import execute_intent
from shared.schema import EditResponse


# ---------------------------------------------------------------------------
# System prompt with 10 required labeled few-shot examples
# ---------------------------------------------------------------------------

CLASSIFY_SYSTEM_PROMPT = """\
You are an intelligent video editor assistant. Given a user's free-text edit command,
classify it into a structured EditIntent. Always respond with a valid JSON object.
Do NOT wrap output in markdown fences.

Required fields: action, target, parameters, confidence.

Valid actions:
  change_scene_mood, rewrite_dialogue, change_visual_style, apply_filter,
  change_bgm, adjust_pacing, regenerate_image, change_voice, add_subtitle, revert_version

Few-shot examples (input → JSON output):

1. "Make scene 2 feel more joyful"
   {"action":"change_scene_mood","target":"scene_002","parameters":{"mood":"joyful"},"confidence":0.95}

2. "Apply a grayscale filter to all images"
   {"action":"apply_filter","target":"all","parameters":{"filter":"grayscale"},"confidence":0.98}

3. "Change Alex's voice to sound older"
   {"action":"change_voice","target":"char_1","parameters":{"voice_id":"en-US-EricNeural"},"confidence":0.82}

4. "Rewrite the first line of dialogue in scene 1 to be more dramatic"
   {"action":"rewrite_dialogue","target":"scene_001","parameters":{"line_index":0,"text":"placeholder — regenerate with LLM"},"confidence":0.88}

5. "Add a sepia tone to the opening scene"
   {"action":"apply_filter","target":"scene_001","parameters":{"filter":"sepia"},"confidence":0.91}

6. "Make the background music in scene 3 more tense"
   {"action":"change_bgm","target":"scene_003","parameters":{"mood":"tense"},"confidence":0.93}

7. "Speed up the middle scene"
   {"action":"adjust_pacing","target":"scene_002","parameters":{"delta_seconds":-5.0},"confidence":0.80}

8. "Regenerate the image for scene 4"
   {"action":"regenerate_image","target":"scene_004","parameters":{},"confidence":0.99}

9. "Add subtitles to the video"
   {"action":"add_subtitle","target":"all","parameters":{},"confidence":0.97}

10. "Go back to version 2"
    {"action":"revert_version","target":"all","parameters":{"version":2},"confidence":0.96}
"""


def _get_llm():
    return get_chat_llm_with_fallback()


# ---------------------------------------------------------------------------
# LangGraph nodes
# ---------------------------------------------------------------------------

class EditState(TypedDict):
    run_id: str
    command: str
    intent: Any          # EditIntent
    changes_made: List[str]
    version: int
    response: Any        # EditResponse


def classify_intent_node(state: EditState) -> EditState:
    llm = _get_llm().with_structured_output(EditIntent)
    messages = [
        SystemMessage(content=CLASSIFY_SYSTEM_PROMPT),
        HumanMessage(content=f'Edit command: "{state["command"]}"'),
    ]
    intent: EditIntent = llm.invoke(messages)
    return {**state, "intent": intent}


def route_execution_node(state: EditState) -> EditState:
    changes = execute_intent(state["intent"], state["run_id"])
    return {**state, "changes_made": changes}


def snapshot_node(state: EditState) -> EditState:
    from shared.state_manager import StateManager
    import json
    from pathlib import Path
    from shared.constants import OUTPUT_DIR

    mgr = StateManager()
    version = mgr.latest_version() + 1

    # Collect current asset paths
    out = Path(OUTPUT_DIR)
    assets = [str(p) for p in out.glob("*.json")] + \
             [str(p) for p in (out / "images").glob("*.png")] + \
             [str(p) for p in (out / "audio").glob("*.wav")] + \
             [str(out / "final_output.mp4")]

    state_json = {"run_id": state["run_id"], "command": state["command"],
                  "intent": state["intent"].model_dump()}
    summary = f"Edit: {state['intent'].action} on {state['intent'].target}"

    mgr.snapshot(version, state["run_id"], state_json, assets, summary=summary)
    return {**state, "version": version}


def respond_node(state: EditState) -> EditState:
    resp = EditResponse(
        intent=state["intent"],
        version=state["version"],
        changes_made=state["changes_made"],
        message=f"Applied '{state['intent'].action}' on '{state['intent'].target}'. "
                f"Saved as version {state['version']}.",
    )
    return {**state, "response": resp}


# ---------------------------------------------------------------------------
# Graph
# ---------------------------------------------------------------------------

def build_edit_graph():
    graph = StateGraph(EditState)
    graph.add_node("classify_intent_node", classify_intent_node)
    graph.add_node("route_execution_node", route_execution_node)
    graph.add_node("snapshot_node", snapshot_node)
    graph.add_node("respond_node", respond_node)

    graph.set_entry_point("classify_intent_node")
    graph.add_edge("classify_intent_node", "route_execution_node")
    graph.add_edge("route_execution_node", "snapshot_node")
    graph.add_edge("snapshot_node", "respond_node")
    graph.add_edge("respond_node", END)
    return graph.compile()


_edit_graph = None


def run_edit(run_id: str, command: str, state_mgr=None) -> EditResponse:
    global _edit_graph
    if _edit_graph is None:
        _edit_graph = build_edit_graph()
    result = _edit_graph.invoke(
        {"run_id": run_id, "command": command, "intent": None,
         "changes_made": [], "version": 0, "response": None},
        config={"configurable": {"thread_id": run_id}},
    )
    return result["response"]
