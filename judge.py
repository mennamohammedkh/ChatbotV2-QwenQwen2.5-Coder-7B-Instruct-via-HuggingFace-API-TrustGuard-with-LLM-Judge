"""
judge.py — LLM-as-Judge using the same HuggingFace model
"""

import json
import logging
from trustguard.judges import BaseJudge
from llm import llm
from config import JUDGE_PROMPT, JUDGE_MAX_TOKENS

logger = logging.getLogger(__name__)


class LLMJudge(BaseJudge):
    """
    Uses the LLM itself to evaluate whether a response is safe.
    Blocks only: hate speech, violence, self-harm, explicit content, malware.
    Allows: coding help, math, general knowledge.
    """

    def judge(self, text: str) -> dict:
        try:
            raw = llm(
                messages=[
                    {"role": "system", "content": JUDGE_PROMPT},
                    {"role": "user",   "content": f"Evaluate this response:\n\n{text}"},
                ],
                max_tokens=JUDGE_MAX_TOKENS,
            )
            s, e = raw.find("{"), raw.rfind("}") + 1
            result = json.loads(raw[s:e])
            logger.debug(f"Judge verdict: {result}")
            return result

        except Exception as e:
            logger.warning(f"Judge parse error: {e} — defaulting to safe")
            return {"safe": True, "reason": "Could not parse judge response", "confidence": 0.5}