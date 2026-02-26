"""
routers/aihelp.py
Exposes /aihelp endpoints. Authenticated users only.
Uses AsyncSession + selectinload to eagerly load relationships.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from auth import get_current_user
from models.user import User
from models.conversation import Conversation, Message
from schemas.aihelp import ChatRequest, ChatResponse, ConversationOut, MessageOut
from services.ai_service import process_text_message
from clients.sarvam_client import transcribe_audio, synthesize_speech

router = APIRouter(prefix="/aihelp", tags=["AI Help"])
templates = Jinja2Templates(directory="templates")


# ── UI Route ───────────────────────────────────────────────────────────────

@router.get("", response_class=HTMLResponse, include_in_schema=False)
async def aihelp_page(request: Request):
    """Renders the chat UI. Auth is enforced client-side by aihelp.js (same pattern as /farmservice)."""
    return templates.TemplateResponse(
        request=request,
        name="aihelp.html",
        context={"title": "AI Assistant"},
    )


# ── Chat Endpoint ──────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Main conversational endpoint.
    POST /aihelp/chat
    Body: {"message": "...", "conversation_id": null}
    """
    if not body.message.strip():
        raise HTTPException(status_code=422, detail="Message cannot be empty.")

    result = await process_text_message(
        user_id=current_user.id,
        user_message=body.message.strip(),
        db=db,
        conversation_id=body.conversation_id,
    )
    return ChatResponse(**result)


# ── Conversation History ───────────────────────────────────────────────────

@router.get("/conversations", response_model=list[ConversationOut])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all conversations for the current user, newest first."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .options(selectinload(Conversation.messages))   # eagerly load — prevents MissingGreenlet
        .order_by(Conversation.created_at.desc())
    )
    return result.scalars().all()


@router.get("/conversations/{conversation_id}", response_model=ConversationOut)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific conversation with all its messages."""
    result = await db.execute(
        select(Conversation)
        .where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .options(selectinload(Conversation.messages))   # eagerly load messages
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return conv


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a conversation and all its messages."""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    await db.delete(conv)
    await db.commit()


# ── Voice Endpoints ────────────────────────────────────────────────────────

@router.post("/voice/chat")
async def voice_chat(
    audio: UploadFile = File(...),
    conversation_id: int = Form(None),
    language: str = Form("hi-IN"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Full voice pipeline:
    1. Sarvam STT  → transcript text
    2. AI pipeline → text response
    3. Sarvam TTS  → audio bytes
    Returns WAV audio directly with transcript/response headers.
    """
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=422, detail="Empty audio file.")

    # STT: audio → text
    try:
        transcript = await transcribe_audio(audio_bytes, language=language, filename=audio.filename or "audio.wav")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"STT failed: {exc}")

    if not transcript.strip():
        raise HTTPException(status_code=422, detail="Could not transcribe audio. Please speak clearly.")

    # LLM pipeline: text → response
    result = await process_text_message(
        user_id=current_user.id,
        user_message=transcript,
        db=db,
        conversation_id=conversation_id,
    )

    # TTS: response text → audio
    try:
        wav_bytes = await synthesize_speech(result["response"], language=language)
    except Exception as exc:
        # On TTS failure, return text response as JSON fallback
        return {
            "transcript": transcript,
            "response": result["response"],
            "conversation_id": result["conversation_id"],
            "tts_error": str(exc),
        }

    return Response(
        content=wav_bytes,
        media_type="audio/wav",
        headers={
            "X-Transcript": transcript[:500],
            "X-Response": result["response"][:500],
            "X-Conversation-Id": str(result["conversation_id"]),
        },
    )


@router.post("/voice/speak")
async def voice_speak(
    text: str = Form(...),
    language: str = Form("en-IN"),
    current_user: User = Depends(get_current_user),
):
    """TTS only: convert text to WAV audio. Used to read out assistant responses."""
    try:
        wav_bytes = await synthesize_speech(text[:500], language=language)
        return Response(content=wav_bytes, media_type="audio/wav")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"TTS failed: {exc}")
