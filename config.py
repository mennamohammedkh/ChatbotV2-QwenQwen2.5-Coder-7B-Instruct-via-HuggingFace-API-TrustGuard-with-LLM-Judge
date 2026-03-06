"""
config.py — Centralized configuration loaded from .env
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Model ──────────────────────────────────────────────────────────────────
MODEL_ID         = os.getenv("MODEL_ID", "Qwen/Qwen2.5-Coder-7B-Instruct")
HF_TOKEN         = os.getenv("HF_TOKEN")
MAX_TOKENS       = int(os.getenv("MAX_TOKENS", 3000))
JUDGE_MAX_TOKENS = int(os.getenv("JUDGE_MAX_TOKENS", 80))

# ── Safety ─────────────────────────────────────────────────────────────────
FOLLOW_UPS = {"yes", "more", "ok", "continue", "go on"}

SYSTEM_PROMPT = (
    "You are a helpful Python coding assistant. "
    "You help developers write code, debug issues, and use Python tools and libraries. "
    "Key tools in this project: "
    "'uv' is a fast modern Python package manager (replaces pip, e.g. 'uv add trustguard'); "
    "'trustguard' is a Python library for LLM output validation and safety guardrails; "
    "'huggingface_hub' is used to call LLM models via the HuggingFace Inference API. "
    "IMPORTANT: You MUST always reply with a single valid JSON object and nothing else. "
    "No markdown, no code blocks, no extra text before or after the JSON. "
    "Use this EXACT format:\n"
    '{"content": "your answer here", "sentiment": "positive", "tone": "helpful", "is_helpful": true}\n'
    'STRICT RULES:\n'
    '- "sentiment" MUST be exactly one of: "positive", "neutral", "negative". NEVER use other words.\n'
    '- "tone" MUST be exactly one of: "helpful", "cautious". NEVER use other words.\n'
    '- "is_helpful" MUST be true or false.\n'
    "- If your answer includes code, put it inside the content string using \\n for newlines."
)

JUDGE_PROMPT = (
    "You are a safety judge. Mark a response as unsafe ONLY if it contains: "
    "hate speech, violence, self-harm, explicit sexual content, or real malware/exploits.\n"
    "Coding help, math, science, and general knowledge are always SAFE. "
    "Technical terms like 'die', 'kill process', 'dead code', 'execute' are normal programming terms — always SAFE.\n"
    'Reply ONLY with JSON: {"safe": true/false, "reason": "...", "confidence": 0.0-1.0}'
)