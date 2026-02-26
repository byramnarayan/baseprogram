"""
services/plantnet_service.py
Calls PlantNet API with plant image bytes, returns top identification result.
Images are NOT stored — only text data is persisted.
"""

import httpx
from typing import Optional, Dict, Any
from config import settings


async def identify_plant(image_bytes: bytes, filename: str) -> Optional[Dict[str, Any]]:
    """
    Sends image to PlantNet API and returns top identification result.
    Returns None if confidence < 0.30 or no results found.
    """
    url = f"{settings.plantnet_base_url}/identify/all"
    params = {"api-key": settings.plantnet_api_key, "lang": "en"}
    files = {"images": (filename, image_bytes, "image/jpeg")}

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, params=params, files=files)

    if resp.status_code not in (200, 201):
        return None

    data = resp.json()
    results = data.get("results", [])
    if not results:
        return None

    top = results[0]
    score = top.get("score", 0)
    if score < 0.30:
        return None  # too uncertain

    species = top.get("species", {})
    sci_name = species.get("scientificNameWithoutAuthor", "Unknown")
    common_list = species.get("commonNames", [])
    common_name = common_list[0] if common_list else sci_name
    family = species.get("family", {}).get("scientificNameWithoutAuthor")

    return {
        "common_name": common_name,
        "scientific_name": sci_name,
        "family": family,
        "confidence": round(score, 4),
    }


def assign_emoji(common_name: str, family: str) -> str:
    """Auto-assign an emoji based on plant type keywords."""
    name = (common_name + " " + (family or "")).lower()
    if any(k in name for k in ["rose", "hibiscus", "tulip"]):      return "🌹"
    if any(k in name for k in ["sunflower", "daisy", "chamomile"]): return "🌻"
    if any(k in name for k in ["cactus", "succulent"]):             return "🌵"
    if any(k in name for k in ["fern", "moss"]):                    return "🌿"
    if any(k in name for k in ["tree", "oak", "pine", "palm"]):     return "🌲"
    if any(k in name for k in ["grass", "bamboo"]):                 return "🎋"
    if any(k in name for k in ["mushroom", "fungi"]):               return "🍄"
    if any(k in name for k in ["lily", "orchid"]):                  return "🌸"
    if any(k in name for k in ["wheat", "rice", "maize", "corn"]):  return "🌾"
    if any(k in name for k in ["mango", "guava", "neem"]):          return "🌳"
    return "🌱"


BADGE_COLORS = [
    "#2D6A4F", "#1B4332", "#40916C", "#52B788",
    "#74C69D", "#31694E", "#BBC863", "#5C7A34",
]

def assign_badge_color(user_id: int, plant_count: int) -> str:
    return BADGE_COLORS[(user_id + plant_count) % len(BADGE_COLORS)]
