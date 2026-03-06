"""
api.py — FastAPI entry point

uv add fastapi uvicorn
uv run uvicorn api:app --reload
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from chatbotV2 import chat
from memory import Memory
from config import FOLLOW_UPS
from guard import guard

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# ── Session Store (in-memory; swap for Redis/DB in production) ─────────────
sessions: dict[str, Memory] = {}


def get_or_create_session(session_id: str) -> Memory:
    if session_id not in sessions:
        sessions[session_id] = Memory()
    return sessions[session_id]


# ── Lifespan ───────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    sessions.clear()


# ── App ────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="ChatGuard — Safe LLM Chatbot",
    description="A safe chatbot powered by Qwen2.5-Coder via HuggingFace API, validated by TrustGuard LLM Judge.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    is_safe: bool


class SessionInfo(BaseModel):
    session_id: str
    last_reply: Optional[str]
    message_count: int


class SessionHistory(BaseModel):
    session_id: str
    history: list[dict]


class SessionList(BaseModel):
    sessions: list[str]
    count: int


class StatsResponse(BaseModel):
    total_validations: int
    approved: int
    rejected: int
    judge_checks: int


# ── Routes ─────────────────────────────────────────────────────────────────

# Health
@app.get("/", tags=["Health"])
def health():
    return {"status": "ok", "service": "ChatGuard", "version": "2.0.0"}


@app.get("/stats", response_model=StatsResponse, tags=["Health"])
def stats():
    """TrustGuard validation statistics."""
    return guard.get_stats()


# Chat
@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
def chat_endpoint(req: ChatRequest):
    """Send a message and get a validated safe response."""
    message = req.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    memory = get_or_create_session(req.session_id)

    # Follow-up shortcut
    if message.lower() in FOLLOW_UPS:
        if memory.last_reply is None:
            return ChatResponse(
                reply="Nothing to expand on yet — ask me something first!",
                session_id=req.session_id,
                is_safe=True,
            )
        message = f"Tell me more about: {memory.last_reply}"

    reply, is_safe = chat(message, memory)

    if not is_safe:
        raise HTTPException(status_code=422, detail=reply)

    return ChatResponse(reply=reply, session_id=req.session_id, is_safe=is_safe)


# Session
@app.get("/sessions", response_model=SessionList, tags=["Session"])
def list_sessions():
    """List all active sessions."""
    return SessionList(sessions=list(sessions.keys()), count=len(sessions))


@app.get("/session/{session_id}", response_model=SessionInfo, tags=["Session"])
def session_info(session_id: str):
    """Get info about a specific session."""
    memory = sessions.get(session_id)
    if memory is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    return SessionInfo(
        session_id=session_id,
        last_reply=memory.last_reply,
        message_count=len(memory.history),
    )


@app.get("/session/{session_id}/history", response_model=SessionHistory, tags=["Session"])
def session_history(session_id: str):
    """Get full conversation history for a session."""
    memory = sessions.get(session_id)
    if memory is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    return SessionHistory(session_id=session_id, history=memory.history)


@app.delete("/session/{session_id}", tags=["Session"])
def delete_session(session_id: str):
    """Delete a session and its history."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found.")
    del sessions[session_id]
    return {"deleted": session_id}