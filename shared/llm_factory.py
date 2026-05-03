"""
shared/llm_factory.py
=====================
Local LLM via Ollama only (free, offline). Configure model with OLLAMA_MODEL in .env.

Good defaults on Apple Silicon / 8GB: llama3.2:3b. Stronger (more RAM): mistral:7b,
qwen2.5:7b, phi3:medium — run `ollama pull <name>` first.
"""

from __future__ import annotations

import logging

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama

from shared.constants import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_NUM_CTX,
    OLLAMA_NUM_PREDICT,
)

logger = logging.getLogger(__name__)


def _make_ollama(temperature: float) -> ChatOllama:
    return ChatOllama(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL,
        temperature=temperature,
        num_predict=OLLAMA_NUM_PREDICT,
        num_ctx=OLLAMA_NUM_CTX,
    )


def get_chat_llm(temperature: float = 0.7) -> BaseChatModel:
    """Return the chat model for Phase 1 / Phase 5 agents (Ollama)."""
    logger.info("Using Ollama model %s at %s", OLLAMA_MODEL, OLLAMA_BASE_URL)
    return _make_ollama(temperature)


def get_chat_llm_with_fallback(temperature: float = 0.7) -> BaseChatModel:
    """Alias for agents that used the old Claude+Ollama wrapper — Ollama only now."""
    return get_chat_llm(temperature=temperature)
