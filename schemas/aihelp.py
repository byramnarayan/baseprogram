"""
NEW FILE: schemas/aihelp.py
Request and response validation for /aihelp endpoints.
Voice-ready: ChatRequest can carry audio fields later.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ── Request ────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str                           # Text input (voice will add audio field later)
    conversation_id: Optional[int] = None  # Continue existing thread; None = new conversation


# ── Response components ─────────────────────────────────────────────────────

class SourceChunk(BaseModel):
    text: str
    score: float
    metadata: Optional[dict] = {}


class ChatResponse(BaseModel):
    response: str
    conversation_id: int
    sources: List[SourceChunk] = []


# ── History ────────────────────────────────────────────────────────────────

class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    timestamp: datetime

    model_config = {"from_attributes": True}


class ConversationOut(BaseModel):
    id: int
    title: Optional[str] = None
    created_at: datetime
    messages: List[MessageOut] = []

    model_config = {"from_attributes": True}
