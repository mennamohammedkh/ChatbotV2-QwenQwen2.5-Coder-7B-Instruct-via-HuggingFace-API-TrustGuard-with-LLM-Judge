"""
llm.py — HuggingFace Inference API client
"""

import logging
from huggingface_hub import InferenceClient
from config import MODEL_ID, HF_TOKEN, MAX_TOKENS

logger = logging.getLogger(__name__)

client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)


def llm(messages: list[dict], max_tokens: int = MAX_TOKENS) -> str:
    """
    Send messages to the LLM and return the response text.
    Raises RuntimeError on API failure.
    """
    try:
        response = client.chat_completion(messages=messages, max_tokens=max_tokens)
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM API error: {e}")
        raise RuntimeError(f"LLM call failed: {e}") from e