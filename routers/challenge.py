"""
routers/challenge.py
Gamified plant discovery: /challenge endpoints.
Fully async — uses AsyncSession throughout.
"""

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from auth import get_current_user
from models.user import User
from models.plant_discovery import PlantDiscovery, UserTree
from schemas.plant import (
    PlantIdentifyResponse, PlantChatRequest, PlantChatResponse,
    StreakResponse, TreeResponse, BadgeOut,
)
from services.plantnet_service import identify_plant, assign_emoji, assign_badge_color
from services.plant_ai_service import generate_fun_fact, chat_about_plant
from services.streak_service import record_verification, get_seven_day_streak

router = APIRouter(prefix="/challenge", tags=["Challenge"])
templates = Jinja2Templates(directory="templates")


# ── HTML Page ────────────────────────────────────────────────────────────────

@router.get("", response_class=HTMLResponse)
async def challenge_page(request: Request):
    """Challenge page — auth enforced client-side (same pattern as /aihelp)."""
    return templates.TemplateResponse(
        request=request,
        name="challenge.html",
        context={"title": "Daily Plant Challenge"},
    )


# ── Plant Identification ─────────────────────────────────────────────────────

@router.post("/identify", response_model=PlantIdentifyResponse)
async def identify(
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Full identification pipeline:
    1. Read image bytes (NOT stored)
    2. Send to PlantNet API
    3. Generate fun fact via Sarvam
    4. Save PlantDiscovery (text only)
    5. Update DailyStreak + UserTree
    """
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=422, detail="Please upload an image file.")

    image_bytes = await image.read()
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image too large. Max 10MB.")

    # PlantNet identification
    result = await identify_plant(image_bytes, image.filename or "plant.jpg")
    if not result:
        raise HTTPException(
            status_code=422,
            detail="Could not identify this plant with sufficient confidence. Try a clearer photo!",
        )

    common_name = result["common_name"]
    scientific_name = result["scientific_name"]
    family = result["family"]
    confidence = result["confidence"]

    # Check if this is a first-ever global discovery
    global_result = await db.execute(
        select(PlantDiscovery).where(PlantDiscovery.scientific_name == scientific_name).limit(1)
    )
    is_first_global = global_result.scalar_one_or_none() is None

    # Check if user already has this species
    user_result = await db.execute(
        select(PlantDiscovery).where(
            PlantDiscovery.user_id == current_user.id,
            PlantDiscovery.scientific_name == scientific_name,
        )
    )
    user_existing = user_result.scalar_one_or_none()

    # Generate fun fact
    fun_fact = await generate_fun_fact(common_name, scientific_name)

    if user_existing:
        # Re-discovery: update fun fact & confidence if better
        user_existing.fun_fact = fun_fact
        if confidence > (user_existing.confidence or 0):
            user_existing.confidence = confidence
        await db.commit()
        discovery_id = user_existing.id
        points = 5
    else:
        # New discovery for this user
        badge_count_result = await db.execute(
            select(func.count()).where(PlantDiscovery.user_id == current_user.id)
        )
        badge_count = badge_count_result.scalar() or 0
        points = 40 if is_first_global else 10

        discovery = PlantDiscovery(
            user_id=current_user.id,
            common_name=common_name,
            scientific_name=scientific_name,
            family=family,
            confidence=confidence,
            is_first_global=is_first_global,
            points_earned=points,
            fun_fact=fun_fact,
            emoji=assign_emoji(common_name, family or ""),
            badge_color=assign_badge_color(current_user.id, badge_count),
        )
        db.add(discovery)
        await db.commit()
        await db.refresh(discovery)
        discovery_id = discovery.id

    # Update streak + tree
    await record_verification(db=db, user_id=current_user.id)

    return PlantIdentifyResponse(
        common_name=common_name,
        scientific_name=scientific_name,
        family=family,
        confidence=confidence,
        fun_fact=fun_fact,
        is_first_global=is_first_global,
        points_earned=points,
        discovery_id=discovery_id,
        emoji=assign_emoji(common_name, family or ""),
    )


# ── Plant Chat ───────────────────────────────────────────────────────────────

@router.post("/chat", response_model=PlantChatResponse)
async def plant_chat(
    body: PlantChatRequest,
    current_user: User = Depends(get_current_user),
):
    """Chat with Sarvam AI about a specific identified plant."""
    response = await chat_about_plant(
        plant_name=body.plant_name,
        user_message=body.message,
        conversation_history=[],
    )
    return PlantChatResponse(response=response)


# ── Data Endpoints ───────────────────────────────────────────────────────────

@router.get("/streak", response_model=StreakResponse)
async def get_streak(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_seven_day_streak(db=db, user_id=current_user.id)


@router.get("/streak/mini", response_model=StreakResponse)
async def get_streak_mini(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lightweight endpoint for dashboard widget."""
    return await get_seven_day_streak(db=db, user_id=current_user.id)


@router.get("/tree", response_model=TreeResponse)
async def get_tree(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserTree).where(UserTree.user_id == current_user.id)
    )
    tree = result.scalar_one_or_none()
    if not tree:
        return TreeResponse(total_leaves=0, total_points=0, tree_level=1)
    return TreeResponse(
        total_leaves=tree.total_leaves,
        total_points=tree.total_points,
        tree_level=tree.tree_level,
    )


@router.get("/badges", response_model=list[BadgeOut])
async def get_badges(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PlantDiscovery)
        .where(PlantDiscovery.user_id == current_user.id)
        .order_by(PlantDiscovery.discovered_at.desc())
    )
    return result.scalars().all()
