"""
models/plant_discovery.py
NEW: PlantDiscovery, DailyStreak, UserTree ORM models.
Uses async-compatible Mapped[] style matching the existing project.
"""

from datetime import datetime, date
from sqlalchemy import Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class PlantDiscovery(Base):
    """One unique plant species identified by a user. Stored as text only — no images."""
    __tablename__ = "plant_discoveries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    common_name: Mapped[str] = mapped_column(String(200), nullable=False)
    scientific_name: Mapped[str] = mapped_column(String(200), nullable=False)
    family: Mapped[str | None] = mapped_column(String(100), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    emoji: Mapped[str | None] = mapped_column(String(10), nullable=True)
    badge_color: Mapped[str] = mapped_column(String(20), default="#31694E")

    is_first_global: Mapped[bool] = mapped_column(Boolean, default=False)
    points_earned: Mapped[int] = mapped_column(Integer, default=10)
    discovered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    fun_fact: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="plant_discoveries")  # type: ignore


class DailyStreak(Base):
    """One record per day the user verified at least one plant."""
    __tablename__ = "daily_streaks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    streak_date: Mapped[date] = mapped_column(Date, nullable=False)
    plant_count: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="daily_streaks")  # type: ignore


class UserTree(Base):
    """Per-user virtual growing tree. total_leaves = total plants ever verified."""
    __tablename__ = "user_trees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    total_leaves: Mapped[int] = mapped_column(Integer, default=0)
    total_points: Mapped[int] = mapped_column(Integer, default=0)
    tree_level: Mapped[int] = mapped_column(Integer, default=1)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="user_tree", uselist=False)  # type: ignore
