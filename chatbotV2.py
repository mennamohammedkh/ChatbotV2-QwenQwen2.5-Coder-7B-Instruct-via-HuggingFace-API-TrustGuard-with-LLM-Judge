"""
chatbot.py — Core chat logic (UI-agnostic)
"""

import json
import logging
from llm import llm
from guard import guard
from memory import Memory
from config import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


def parse_json(raw: str) -> str:
    """Extract and validate JSON from raw LLM output. Falls back to plain text wrap."""
    try:
        s, e = raw.find("{"), raw.rfind("}") + 1
        json_str = raw[s:e]
        json.loads(json_str)  # validate
        return json_str
    except Exception:
        return json.dumps({
            "content": raw.strip(),
            "sentiment": "neutral",
            "tone": "helpful",
            "is_helpful": True,
        })


def chat(user_message: str, memory: Memory) -> tuple[str, bool]:
    """
    Process a user message and return (reply, is_safe).
    Updates memory in place.
    """
    memory.add_user(user_message)
    messages = memory.get_messages(SYSTEM_PROMPT)

    try:
        raw = llm(messages)
    except RuntimeError as e:
        memory.remove_last()
        return f"⚠️ API error: {e}", False

    json_str = parse_json(raw)
    result = guard.validate(json_str)

    if result.is_approved:
        reply = result.data.get("content", raw.strip())
        memory.add_assistant(reply)
        logger.info("Response approved")
        return reply, True
    else:
        memory.remove_last()
        logger.warning(f"Response blocked: {result.log}")
        return f"🛑 Blocked — {result.log}", False