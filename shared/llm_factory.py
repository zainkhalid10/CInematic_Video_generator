"""
shared/llm_factory.py
=====================
Central LLM selection per project specification §5.2:
  • Primary: Claude (Anthropic API) when ANTHROPIC_API_KEY is set.
  • Fallback: Ollama (local) when no key, import failure, or Claude auth error on first call.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_ollama import ChatOllama

from shared.constants import ANTHROPIC_MODEL, OLLAMA_BASE_URL, OLLAMA_MODEL

logger = logging.getLogger(__name__)

def _make_ollama(temperature: float) -> ChatOllama:
    return ChatOllama(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL,
        temperature=temperature,
    )


def get_chat_llm(temperature: float = 0.7) -> BaseChatModel:
    """
    Return the chat model for agents. Prefers Claude; uses Ollama if no API key
    or if langchain-anthropic is not installed.
    """
    key = (os.getenv("ANTHROPIC_API_KEY") or "").strip()
    if not key:
        logger.info("No ANTHROPIC_API_KEY — using Ollama (%s).", OLLAMA_MODEL)
        return _make_ollama(temperature)

    try:
        from langchain_anthropic import ChatAnthropic

        logger.info("Using Anthropic Claude (%s).", ANTHROPIC_MODEL)
        return ChatAnthropic(
            model=ANTHROPIC_MODEL,
            temperature=temperature,
            max_tokens=8192,
        )
    except ImportError:
        logger.warning("langchain-anthropic not installed — using Ollama (%s).", OLLAMA_MODEL)
        return _make_ollama(temperature)


class _ChatWithOllamaFallback:
    """Wraps a chat model; on auth / rate-limit style errors, retry with Ollama once."""

    def __init__(self, primary: BaseChatModel, temperature: float):
        self._primary = primary
        self._temperature = temperature
        self._fallback: ChatOllama | None = None

    def _get_fallback(self) -> ChatOllama:
        if self._fallback is None:
            self._fallback = _make_ollama(self._temperature)
        return self._fallback

    def with_structured_output(self, schema: Any, **kwargs: Any):
        inner_primary = self._primary.with_structured_output(schema, **kwargs)
        inner_fallback = self._get_fallback().with_structured_output(schema, **kwargs)

        class _Bound:
            def invoke(self, messages: list[BaseMessage], **kw: Any):
                try:
                    return inner_primary.invoke(messages, **kw)
                except Exception as e:
                    err = f"{type(e).__name__}: {e}"
                    if _should_fallback_to_ollama(e):
                        logger.warning(
                            "Claude request failed (%s); retrying with Ollama (%s).",
                            err,
                            OLLAMA_MODEL,
                        )
                        return inner_fallback.invoke(messages, **kw)
                    raise

        return _Bound()

    # Allow direct access if needed
    @property
    def primary(self) -> BaseChatModel:
        return self._primary


def _should_fallback_to_ollama(exc: Exception) -> bool:
    """Heuristic: auth, payment, and invalid-key errors → local Ollama."""
    name = type(exc).__name__.lower()
    msg = str(exc).lower()
    if "authentication" in name or "auth" in msg or "401" in msg:
        return True
    if "permission" in msg or "403" in msg:
        return True
    if "invalid" in msg and "api" in msg:
        return True
    if "rate" in msg and "limit" in msg:
        return True
    if "credit" in msg or "billing" in msg:
        return True
    return False


def get_chat_llm_with_fallback(
    temperature: float = 0.7,
) -> BaseChatModel | _ChatWithOllamaFallback:
    """
    Like get_chat_llm(), but wraps Claude so the first invoke failure matching
    common API-key / quota issues automatically retries on Ollama (spec §5.2).
    """
    primary = get_chat_llm(temperature=temperature)
    if isinstance(primary, ChatOllama):
        return primary
    return _ChatWithOllamaFallback(primary, temperature)
