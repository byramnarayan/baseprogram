"""
schemas/plant.py
Request/response Pydantic schemas for plant challenge endpoints.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class PlantIdentifyResponse(BaseModel):
    common_name: str
    scientific_name: str
    family: Optional[str]
    confidence: float
    fun_fact: Optional[str]
    is_first_global: bool
    points_earned: int
    discovery_id: int
    emoji: str


class PlantChatRequest(BaseModel):
    message: str
    plant_name: str
    discovery_id: int


class PlantChatResponse(BaseModel):
    response: str


class StreakDay(BaseModel):
    date: date
    verified: bool
    plant_count: int


class StreakResponse(BaseModel):
    days: List[StreakDay]
    current_streak: int
    total_days: int


class TreeResponse(BaseModel):
    total_leaves: int
    total_points: int
    tree_level: int


class BadgeOut(BaseModel):
    id: int
    common_name: str
    scientific_name: str
    emoji: str
    badge_color: str
    confidence: float
    is_first_global: bool
    points_earned: int
    discovered_at: datetime
    fun_fact: Optional[str]

    model_config = {"from_attributes": True}
