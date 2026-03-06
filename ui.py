"""
ui.py — Professional Gradio Web UI for ChatGuard
"""

import json
import gradio as gr
from chatbotV2 import chat
from llm import llm
from guard import guard
from memory import Memory
from config import SYSTEM_PROMPT

# ── Theme ─────────────────────────────────────────────────────
THEME = gr.themes.Base(
    primary_hue=gr.themes.colors.purple,
    neutral_hue=gr.themes.colors.slate,
    font=[gr.themes.GoogleFont("DM Sans"), "sans-serif"],
    font_mono=[gr.themes.GoogleFont("JetBrains Mono"), "monospace"],
)

# ── CSS ───────────────────────────────────────────────────────
CSS = """
body, .gradio-container { 
    background:#1A1B26 !important; 
    font-family:'DM Sans', sans-serif;
    color: white;
}

.sidebar { 
    border-right:1px solid #2A3A5C; 
    padding:1rem;
    background-color: #1E1F2D;
}

.stats-panel { font-size:0.85rem; color: #D1D5DB;}
.stat-item { display:flex; justify-content:space-between; padding:4px 0; }
.stat-value { font-weight:bold; color: #F3F4F6; }

.verdict-safe { 
    background:#16A34A; 
    border:1px solid #15803D; 
    padding:10px; 
    border-radius:8px; 
    color:#E0F2FE; 
}

.verdict-blocked { 
    background:#EF4444; 
    border:1px solid #9B1C1C; 
    padding:10px; 
    border-radius:8px; 
    color:#F1F5F9; 
}

.verdict-waiting { 
    background:#1F2937; 
    border:1px solid #4B5563; 
    padding:10px; 
    border-radius:8px; 
    color:#94A3B8; 
}

.chatbot-container {
    height: 400px !important;  /* Reduced height for chatbot */
    overflow-y: auto;  /* Allow scrolling */
    background-color: #2A2F45;
    padding: 10px;
    border-radius: 10px;
}

.chatbot-user {
    background-color: #22D3EE;  /* Cyan color */
    color: #1E40AF;
    border-radius: 12px;
    padding: 8px 15px;
    max-width: 70%;
    margin-bottom: 10px;
    display: inline-block;
    align-self: flex-start;
}

.chatbot-assistant {
    background-color: #9F7AEA;  /* Light purple color */
    color: white;
    border-radius: 12px;
    padding: 8px 15px;
    max-width: 70%;
    margin-bottom: 10px;
    display: inline-block;
    align-self: flex-end;
}

button {
    background-color: #4F46E5;
    color: white;
    border-radius: 8px;
    padding: 10px;
    transition: background-color 0.3s ease;
}

button:hover {
    background-color: #4338CA;
}
"""

# ── Helpers ───────────────────────────────────────────────────
def create_memory(): return Memory()

def parse_json_response(raw: str):
    try:
        s, e = raw.find("{"), raw.rfind("}") + 1
        j = raw[s:e]
        json.loads(j)
        return j
    except Exception:
        return json.dumps({"content": raw.strip(), "sentiment": "neutral", "tone": "helpful", "is_helpful": True})

def get_stats_html():
    s = guard.get_stats()
    return f"""
    <div class="stats-panel">
        <div class="stat-item"><span>Total</span><span class="stat-value">{s['total_validations']}</span></div>
        <div class="stat-item"><span>Approved</span><span class="stat-value" style="color:#16A34A">{s['approved']}</span></div>
        <div class="stat-item"><span>Blocked</span><span class="stat-value" style="color:#EF4444">{s['rejected']}</span></div>
        <div class="stat-item"><span>Judge Calls</span><span class="stat-value">{s['judge_checks']}</span></div>
    </div>
    """

# ── Core Chat Logic ───────────────────────────────────────────
def respond(user_message, history, memory_state):
    if not user_message.strip():
        yield history, memory_state, "", '<div class="verdict-waiting">Waiting...</div>', get_stats_html()
        return

    history.append({"role":"user","content":user_message})
    yield history, memory_state, "", '<div class="verdict-waiting">Thinking...</div>', get_stats_html()
    memory_state.add_user(user_message)
    messages = memory_state.get_messages(SYSTEM_PROMPT)

    try:
        raw = llm(messages)
    except RuntimeError as e:
        memory_state.remove_last()
        history.append({"role":"assistant","content":f"⚠️ API error: {e}"})
        yield history, memory_state, "", '<div class="verdict-blocked">API Error</div>', get_stats_html()
        return

    json_str = parse_json_response(raw)
    result = guard.validate(json_str)

    if result.is_approved:
        reply = result.data.get("content", raw.strip())
        memory_state.add_assistant(reply)
        history.append({"role":"assistant","content":""})
        streamed = ""
        verdict_html = '<div class="verdict-safe">✅ APPROVED</div>'
        for word in reply.split():
            streamed += word + " "
            history[-1]["content"] = streamed
            yield history, memory_state, "", verdict_html, get_stats_html()
    else:
        memory_state.remove_last()
        history.append({"role":"assistant","content":"🛑 Response blocked by safety guard"})
        verdict_html = '<div class="verdict-blocked">🛑 BLOCKED</div>'
        yield history, memory_state, "", verdict_html, get_stats_html()

def clear_chat(memory_state):
    memory_state.clear()
    return [], memory_state, "", '<div class="verdict-waiting">Chat cleared</div>', get_stats_html()

# ── UI Layout ─────────────────────────────────────────────────
with gr.Blocks(title="ChatGuard — Safe LLM Chatbot", theme=THEME, css=CSS) as demo:
    memory_state = gr.State(create_memory)

    with gr.Row():
        # Sidebar
        with gr.Column(scale=1, elem_classes="sidebar"):
            gr.Markdown("## 🛡️ ChatGuard")
            gr.Markdown("AI chatbot with **Trust Guard safety validation**.")
            clear_btn = gr.Button("🧹 Clear Chat")
            stats_display = gr.HTML(get_stats_html())

        # Main chat
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(height=400, elem_classes="chatbot-container")  # Reduced height for chatbot
            verdict_display = gr.HTML('<div class="verdict-waiting">Waiting...</div>')

            # Input row: textbox + send button inline
            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Ask anything...", 
                    container=False, 
                    scale=4
                )
                send_btn = gr.Button(
                    "Send", 
                    scale=1
                )

            # Example questions
            gr.Examples(
                examples=[
                    "Explain transformers simply",
                    "What is prompt injection?",
                    "How does RAG work?",
                    "Write Python quicksort"
                ],
                inputs=msg_input
            )

            # ── Events (inside Blocks) ──
            msg_input.submit(respond, [msg_input, chatbot, memory_state], [chatbot, memory_state, msg_input, verdict_display, stats_display])
            send_btn.click(respond, [msg_input, chatbot, memory_state], [chatbot, memory_state, msg_input, verdict_display, stats_display])
            clear_btn.click(clear_chat, [memory_state], [chatbot, memory_state, msg_input, verdict_display, stats_display])

# ── Launch ───────────────────────────────────────────────────
if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)