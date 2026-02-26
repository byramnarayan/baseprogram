"""
clients/sarvam_client.py
Async wrapper around Sarvam AI: Chat, Embeddings, STT, TTS.
"""

import httpx
from typing import List, Dict
from config import settings

SARVAM_CHAT_URL = f"{settings.sarvam_base_url}/v1/chat/completions"
SARVAM_EMBED_URL = f"{settings.sarvam_base_url}/v1/embeddings"
SARVAM_STT_URL  = "https://api.sarvam.ai/speech-to-text"
SARVAM_TTS_URL  = "https://api.sarvam.ai/text-to-speech"

_HEADERS = {
    "Authorization": f"Bearer {settings.sarvam_api_key}",
    "Content-Type": "application/json",
}

_AUTH_HEADER = {"api-subscription-key": settings.sarvam_api_key}


async def chat_completion(messages: List[Dict[str, str]], max_tokens: int = 512) -> str:
    """Send messages to Sarvam LLM, return assistant reply."""
    payload = {
        "model": "sarvam-m",
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(SARVAM_CHAT_URL, json=payload, headers=_HEADERS)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()


async def embed_text(text: str) -> List[float]:
    """Get Sarvam embedding vector for a text string."""
    payload = {"model": "sarvam-embed", "input": text}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(SARVAM_EMBED_URL, json=payload, headers=_HEADERS)
        resp.raise_for_status()
        return resp.json()["data"][0]["embedding"]


# ── STT (Speech-to-Text) ───────────────────────────────────────────────────

async def transcribe_audio(audio_bytes: bytes, language: str = "hi-IN", filename: str = "audio.wav") -> str:
    """
    Sarvam STT: Convert audio bytes to text.
    Supports WAV, MP3, OGG, WEBM (< 30 seconds).
    language: BCP-47 code e.g. 'hi-IN', 'en-IN', 'kn-IN', 'ta-IN'
    """
    files = {"file": (filename, audio_bytes, "audio/wav")}
    data = {
        "language_code": language,
        "model": "saarika:v2",
        "with_timestamps": "false",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            SARVAM_STT_URL,
            files=files,
            data=data,
            headers=_AUTH_HEADER,
        )
        resp.raise_for_status()
        result = resp.json()
        return result.get("transcript", "").strip()


# ── TTS (Text-to-Speech) ───────────────────────────────────────────────────

async def synthesize_speech(
    text: str,
    language: str = "hi-IN",
    speaker: str = "meera",
) -> bytes:
    """
    Sarvam TTS: Convert text to audio bytes (WAV).
    speaker options: meera, pavithra, maitreyi, arvind, amol, amartya, etc.
    language: BCP-47 code e.g. 'hi-IN', 'en-IN', 'kn-IN'
    Returns raw WAV bytes.
    """
    import base64

    payload = {
        "inputs": [text[:500]],          # Sarvam TTS: max 500 chars per request
        "target_language_code": language,
        "speaker": speaker,
        "model": "bulbul:v1",
        "enable_preprocessing": True,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            SARVAM_TTS_URL,
            json=payload,
            headers={**_AUTH_HEADER, "Content-Type": "application/json"},
        )
        resp.raise_for_status()
        data = resp.json()
        # Response: {"audios": ["<base64_wav>"]}
        audio_b64 = data["audios"][0]
        return base64.b64decode(audio_b64)
