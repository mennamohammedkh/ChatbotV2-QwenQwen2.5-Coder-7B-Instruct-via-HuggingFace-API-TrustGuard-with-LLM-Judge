"""
memory.py — Conversation history manager
"""


class Memory:
    """Manages the chat history for a single conversation session."""

    def __init__(self):
        self.history: list[dict] = []
        self.last_reply: str | None = None

    def add_user(self, message: str):
        self.history.append({"role": "user", "content": message})

    def add_assistant(self, message: str):
        self.history.append({"role": "assistant", "content": message})
        self.last_reply = message

    def remove_last(self):
        """Remove the last user message (e.g. when response is blocked)."""
        if self.history and self.history[-1]["role"] == "user":
            self.history.pop()

    def get_messages(self, system_prompt: str) -> list[dict]:
        """Return full message list with system prompt prepended."""
        return [{"role": "system", "content": system_prompt}] + self.history

    def clear(self):
        self.history.clear()
        self.last_reply = None