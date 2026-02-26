"""
services/plant_ai_service.py
Sarvam AI chat about identified plants + fun fact generation.
Reuses the existing sarvam_client.
"""

from clients.sarvam_client import chat_completion
from typing import List, Dict

PLANT_ASSISTANT_PROMPT = """You are a friendly botanist assistant named Flora. 
You know everything about plants, gardening, ecology, and traditional Indian plant uses.
Keep responses concise (2-4 sentences), warm, and conversational.
Include one surprising or delightful fact when relevant.
Never use bullet points — speak naturally like a knowledgeable friend."""


async def generate_fun_fact(common_name: str, scientific_name: str) -> str:
    """Generate a 2-sentence fun fact for a newly identified plant."""
    messages = [
        {"role": "system", "content": PLANT_ASSISTANT_PROMPT},
        {"role": "user", "content": (
            f"Tell me one fascinating fun fact about {common_name} "
            f"({scientific_name}) in 2 sentences max."
        )},
    ]
    try:
        return await chat_completion(messages, max_tokens=150)
    except Exception:
        return f"{common_name} is a fascinating plant with unique properties!"


async def chat_about_plant(
    plant_name: str,
    user_message: str,
    conversation_history: List[Dict[str, str]],
) -> str:
    """Single-turn chat about a specific plant. Stateless — client sends history."""
    system = {
        "role": "system",
        "content": (
            f"{PLANT_ASSISTANT_PROMPT}\n\n"
            f"The user just identified: {plant_name}. "
            f"Answer their questions about this plant specifically."
        ),
    }
    messages = [system] + conversation_history[-6:] + [
        {"role": "user", "content": user_message}
    ]
    return await chat_completion(messages, max_tokens=300)
