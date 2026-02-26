"""
services/streak_service.py
Async daily streak and tree growth logic.
Fully adapted to AsyncSession (no sync Session used).
"""

from datetime import date, timedelta
from typing import List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.plant_discovery import DailyStreak, UserTree
from schemas.plant import StreakDay, StreakResponse


async def record_verification(db: AsyncSession, user_id: int) -> None:
    """
    Called after a plant is successfully identified.
    Upserts today's DailyStreak and updates UserTree.
    """
    today = date.today()

    # Upsert today's streak record
    result = await db.execute(
        select(DailyStreak).where(
            DailyStreak.user_id == user_id,
            DailyStreak.streak_date == today,
        )
    )
    streak = result.scalar_one_or_none()

    if streak:
        streak.plant_count += 1
    else:
        streak = DailyStreak(user_id=user_id, streak_date=today, plant_count=1)
        db.add(streak)

    # Upsert user tree
    tree_result = await db.execute(
        select(UserTree).where(UserTree.user_id == user_id)
    )
    tree = tree_result.scalar_one_or_none()

    if not tree:
        tree = UserTree(user_id=user_id, total_leaves=0, total_points=0, tree_level=1)
        db.add(tree)

    tree.total_leaves += 1
    tree.total_points += 10
    tree.tree_level = _calc_level(tree.total_leaves)

    await db.commit()


async def get_seven_day_streak(db: AsyncSession, user_id: int) -> StreakResponse:
    """Returns streak data for today + the previous 6 days."""
    today = date.today()
    days_range = [today - timedelta(days=i) for i in range(6, -1, -1)]

    result = await db.execute(
        select(DailyStreak).where(
            DailyStreak.user_id == user_id,
            DailyStreak.streak_date.in_(days_range),
        )
    )
    streak_records = result.scalars().all()
    record_map = {r.streak_date: r.plant_count for r in streak_records}

    days = [
        StreakDay(
            date=d,
            verified=d in record_map,
            plant_count=record_map.get(d, 0),
        )
        for d in days_range
    ]

    # Consecutive streak ending today (walk backwards)
    current_streak = 0
    for d in reversed(days_range):
        if d in record_map:
            current_streak += 1
        else:
            break

    # Total distinct days ever
    count_result = await db.execute(
        select(func.count()).where(DailyStreak.user_id == user_id)
    )
    total_days = count_result.scalar() or 0

    return StreakResponse(days=days, current_streak=current_streak, total_days=total_days)


def _calc_level(leaves: int) -> int:
    """Every 5 plants = next level, max 10."""
    return min(10, max(1, (leaves // 5) + 1))
