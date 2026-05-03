"""
shared/llm_json.py
==================
Fast path for local Ollama: plain chat completion + JSON parse + Pydantic validate.

LangChain's ``with_structured_output`` on Ollama often causes very long runs or
truncated output when ``num_predict`` is too small; this module avoids that.
"""

from __future__ import annotations

import json
import re
import time
from typing import TypeVar

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

_THINKING_RE = re.compile(
    r"<(?:think|redacted_thinking|reasoning)>[\s\S]*?</(?:think|redacted_thinking|reasoning)>",
    re.IGNORECASE,
)


def strip_thinking_blocks(text: str) -> str:
    return _THINKING_RE.sub("", text)


def extract_first_json_value(text: str) -> tuple[object, int]:
    """Find first JSON object or array and decode; return (value, end_index)."""
    text = strip_thinking_blocks(text).strip()
    decoder = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch in "{[":
            try:
                return decoder.raw_decode(text, idx=i)
            except json.JSONDecodeError:
                continue
    preview = text[:800].replace("\n", " ")
    raise ValueError(f"No valid JSON in model output ({len(text)} chars): {preview!r}...")


def message_text(resp: BaseMessage) -> str:
    raw = getattr(resp, "content", "") or ""
    if isinstance(raw, str):
        return raw
    if isinstance(raw, list):
        parts: list[str] = []
        for block in raw:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and "text" in block:
                parts.append(str(block["text"]))
            else:
                parts.append(str(block))
        return "".join(parts)
    return str(raw)


def invoke_json_model(
    llm: BaseChatModel,
    messages: list[BaseMessage],
    result_model: type[T],
    *,
    step_name: str,
    max_retries: int = 3,
) -> T:
    """Call ``llm.invoke``, parse first JSON value, validate as ``result_model``."""
    conversation: list[BaseMessage] = list(messages)
    last_err: Exception | None = None

    for attempt in range(1, max_retries + 1):
        t0 = time.perf_counter()
        try:
            resp = llm.invoke(conversation)
            content = message_text(resp)
            dt = time.perf_counter() - t0
            print(
                f"[LLM] {step_name}: generation {dt:.1f}s, {len(content)} chars (attempt {attempt}/{max_retries})"
            )
            data, _ = extract_first_json_value(content)
            return result_model.model_validate(data)
        except (ValueError, json.JSONDecodeError, ValidationError) as e:
            last_err = e
            print(f"[LLM] {step_name}: parse/validate error: {e}")
            if attempt >= max_retries:
                break
            conversation = list(conversation) + [
                HumanMessage(
                    content=(
                        "Your last reply was not valid JSON for the schema. "
                        f"Error: {e}\n"
                        "Reply again with ONLY one JSON object (or array if asked), no markdown fences, no commentary."
                    )
                ),
            ]
    raise RuntimeError(f"{step_name} failed after {max_retries} attempts: {last_err}") from last_err
