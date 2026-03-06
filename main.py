"""
main.py — Terminal entry point

uv run python main.py
"""

import logging
from chatbotV2 import chat
from memory import Memory
from config import FOLLOW_UPS

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

def main():
    memory = Memory()

    print("╔══════════════════════════════════════╗")
    print("║   🤖 ChatGuard  — Safe LLM Chatbot   ║")
    print("║          type 'quit' to exit         ║")
    print("╚══════════════════════════════════════╝\n")

    while True:
        try:
            user = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break

        if not user or user.lower() in ("quit", "exit"):
            print("👋 Goodbye!")
            break

        # Follow-up shortcut
        if user.lower() in FOLLOW_UPS:
            if memory.last_reply is None:
                print("Bot: Nothing to expand on yet — ask me something first!\n")
                continue
            user = f"Tell me more about: {memory.last_reply}"

        reply, _ = chat(user, memory)
        print(f"Bot: {reply}\n")


if __name__ == "__main__":
    main()