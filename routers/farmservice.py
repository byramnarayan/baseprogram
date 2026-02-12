"""
Farm Service Router

This module handles all farm-related API endpoints:
- GET /farmservice: Render farmservice HTML page
- GET /api/farmservice/farms: List all farms for current user
- POST /api/farmservice/farms: Create new farm
- GET /api/farmservice/farms/{farm_id}: Get single farm
- PUT /api/farmservice/farms/{farm_id}: Update farm
- DELETE /api/farmservice/farms/{farm_id}: Delete farm
- GET /api/farmservice/statistics: Get dashboard statistics

All API routes are protected and require authentication.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from database import get_db
from models.farm import Farm
from models.user import User
from schemas.farm import (
    FarmCreate,
    FarmUpdate,
    FarmResponse,
    FarmStatistics,
    FarmListResponse,
)
from utils.geospatial import calculate_area_from_polygon, get_polygon_center
from utils.carbon_calculator import calculate_annual_credits, calculate_annual_value


# Create router
router = APIRouter()

# Templates for HTML pages
templates = Jinja2Templates(directory="templates")


# ============================================================================
# HTML Page Route
# ============================================================================

@router.get("/farmservice", include_in_schema=False)
async def farmservice_page(request: Request):
    """
    Render the farm service dashboard page.
    
    This is a protected page - frontend JavaScript will check authentication
    and redirect to login if no token is found.
    
    Returns:
        HTML: Rendered farmservice.html template
    """
    return templates.TemplateResponse(
        request=request,
        name="farmservice.html",
        context={"title": "Farm Service"}
    )


# ============================================================================
# API Endpoints (Protected)
# ============================================================================

@router.get("/api/farmservice/farms", response_model=FarmListResponse)
async def get_all_farms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all farms for the current authenticated user.
    
    Returns farm data along with aggregated statistics for dashboard display.
    
    Args:
        current_user: Authenticated user (injected by dependency)
        db: Database session (injected by dependency)
        
    Returns:
        FarmListResponse: List of farms with summary statistics
        
    Example Response:
        {
            "summary": {
                "total_farms": 5,
                "total_area_hectares": 12.5,
                "total_annual_credits": 156.25,
                "total_annual_value_inr": 78125.0,
                "verified_farms": 3,
                "pending_verification": 2
            },
            "farms": [...]
        }
    """
    # Fetch all farms for the current user
    result = await db.execute(
        select(Farm).where(Farm.farmer_id == current_user.id).order_by(Farm.created_at.desc())
    )
    farms = result.scalars().all()
    
    # Calculate summary statistics
    total_farms = len(farms)
    total_area = sum(farm.area_hectares for farm in farms)
    total_credits = sum(farm.annual_credits for farm in farms)
    total_value = sum(farm.annual_value_inr for farm in farms)
    verified_count = sum(1 for farm in farms if farm.is_verified)
    pending_count = total_farms - verified_count
    
    # Build response
    summary = FarmStatistics(
        total_farms=total_farms,
        total_area_hectares=round(total_area, 2),
        total_annual_credits=round(total_credits, 2),
        total_annual_value_inr=round(total_value, 2),
        verified_farms=verified_count,
        pending_verification=pending_count,
    )
    
    return FarmListResponse(
        summary=summary,
        farms=[FarmResponse.model_validate(farm) for farm in farms]
    )


@router.post(
    "/api/farmservice/farms",
    response_model=FarmResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_farm(
    farm_data: FarmCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new farm for the authenticated user.
    
    Process:
    1. Validate input data (Pydantic schema)
    2. Calculate area from polygon coordinates
    3. Calculate center coordinates
    4. Calculate carbon credits based on area and soil type
    5. Save to database
    6. Return created farm
    
    Args:
        farm_data: Farm creation data
        current_user: Authenticated user
        db: Database session
        
    Returns:
        FarmResponse: Created farm with calculated fields
        
    Raises:
        HTTPException 400: If polygon is invalid
        HTTPException 422: If validation fails
    """
    try:
        # Calculate area from polygon coordinates
        area_hectares = calculate_area_from_polygon(farm_data.polygon_coordinates)
        
        # Calculate center point
        center_lat, center_lon = get_polygon_center(farm_data.polygon_coordinates)
        
        # Calculate carbon credits (unverified farms get 50% credits)
        annual_credits = calculate_annual_credits(
            area_hectares=area_hectares,
            soil_type=farm_data.soil_type,
            is_verified=False,  # New farms start unverified
        )
        
        # Calculate monetary value
        annual_value = calculate_annual_value(annual_credits)
        
        # Create farm object
        new_farm = Farm(
            farmer_id=current_user.id,
            farm_name=farm_data.farm_name,
            phone=farm_data.phone,
            latitude=center_lat,
            longitude=center_lon,
            area_hectares=area_hectares,
            soil_type=farm_data.soil_type,
            district=farm_data.district,
            state=farm_data.state,
            annual_credits=annual_credits,
            annual_value_inr=annual_value,
            polygon_coordinates=farm_data.polygon_coordinates,
            is_verified=False,
        )
        
        # Save to database
        db.add(new_farm)
        await db.commit()
        await db.refresh(new_farm)
        
        return FarmResponse.model_validate(new_farm)
        
    except ValueError as e:
        # Validation error from geospatial utilities
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Unexpected error
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create farm: {str(e)}"
        )


@router.get("/api/farmservice/farms/{farm_id}", response_model=FarmResponse)
async def get_farm(
    farm_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific farm by ID.
    
    Only the farm owner can access their farm data.
    
    Args:
        farm_id: ID of the farm to retrieve
        current_user: Authenticated user
        db: Database session
        
    Returns:
        FarmResponse: Farm data
        
    Raises:
        HTTPException 404: If farm not found
        HTTPException 403: If user is not the farm owner
    """
    # Fetch farm
    result = await db.execute(select(Farm).where(Farm.id == farm_id))
    farm = result.scalar_one_or_none()
    
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} not found"
        )
    
    # Verify ownership
    if farm.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this farm"
        )
    
    return FarmResponse.model_validate(farm)


@router.put("/api/farmservice/farms/{farm_id}", response_model=FarmResponse)
async def update_farm(
    farm_id: int,
    farm_data: FarmUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update an existing farm.
    
    Only the farm owner can update their farm.
    If polygon coordinates are updated, area and credits are recalculated.
    
    Args:
        farm_id: ID of the farm to update
        farm_data: Updated farm data (partial update)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        FarmResponse: Updated farm data
        
    Raises:
        HTTPException 404: If farm not found
        HTTPException 403: If user is not the farm owner
        HTTPException 400: If validation fails
    """
    # Fetch farm
    result = await db.execute(select(Farm).where(Farm.id == farm_id))
    farm = result.scalar_one_or_none()
    
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} not found"
        )
    
    # Verify ownership
    if farm.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this farm"
        )
    
    try:
        # Track if we need to recalculate area/credits
        recalculate_area = False
        recalculate_credits = False
        
        # Update provided fields
        if farm_data.farm_name is not None:
            farm.farm_name = farm_data.farm_name
        
        if farm_data.phone is not None:
            farm.phone = farm_data.phone
        
        if farm_data.district is not None:
            farm.district = farm_data.district
        
        if farm_data.state is not None:
            farm.state = farm_data.state
        
        if farm_data.soil_type is not None:
            farm.soil_type = farm_data.soil_type
            recalculate_credits = True
        
        if farm_data.polygon_coordinates is not None:
            farm.polygon_coordinates = farm_data.polygon_coordinates
            recalculate_area = True
            recalculate_credits = True
        
        # Recalculate area if polygon changed
        if recalculate_area:
            farm.area_hectares = calculate_area_from_polygon(farm.polygon_coordinates)
            center_lat, center_lon = get_polygon_center(farm.polygon_coordinates)
            farm.latitude = center_lat
            farm.longitude = center_lon
        
        # Recalculate credits if area or soil type changed
        if recalculate_credits:
            farm.annual_credits = calculate_annual_credits(
                area_hectares=farm.area_hectares,
                soil_type=farm.soil_type,
                is_verified=farm.is_verified,
            )
            farm.annual_value_inr = calculate_annual_value(farm.annual_credits)
        
        # Save changes
        await db.commit()
        await db.refresh(farm)
        
        return FarmResponse.model_validate(farm)
        
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update farm: {str(e)}"
        )


@router.delete("/api/farmservice/farms/{farm_id}")
async def delete_farm(
    farm_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a farm.
    
    Only the farm owner can delete their farm.
    This is a hard delete - the farm is permanently removed from the database.
    
    Args:
        farm_id: ID of the farm to delete
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException 404: If farm not found
        HTTPException 403: If user is not the farm owner
    """
    # Fetch farm
    result = await db.execute(select(Farm).where(Farm.id == farm_id))
    farm = result.scalar_one_or_none()
    
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} not found"
        )
    
    # Verify ownership
    if farm.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this farm"
        )
    
    # Delete farm
    await db.delete(farm)
    await db.commit()
    
    return {
        "message": f"Farm '{farm.display_name}' deleted successfully",
        "deleted_farm_id": farm_id
    }


@router.get("/api/farmservice/statistics", response_model=FarmStatistics)
async def get_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get aggregated statistics for the current user's farms.
    
    Returns summary information for dashboard display.
    This endpoint is separate from the farms list for cases where
    only statistics are needed (e.g., dashboard widget).
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        FarmStatistics: Aggregated statistics
    """
    # Fetch all farms for the current user
    result = await db.execute(
        select(Farm).where(Farm.farmer_id == current_user.id)
    )
    farms = result.scalars().all()
    
    # Calculate statistics
    total_farms = len(farms)
    total_area = sum(farm.area_hectares for farm in farms)
    total_credits = sum(farm.annual_credits for farm in farms)
    total_value = sum(farm.annual_value_inr for farm in farms)
    verified_count = sum(1 for farm in farms if farm.is_verified)
    pending_count = total_farms - verified_count
    
    return FarmStatistics(
        total_farms=total_farms,
        total_area_hectares=round(total_area, 2),
        total_annual_credits=round(total_credits, 2),
        total_annual_value_inr=round(total_value, 2),
        verified_farms=verified_count,
        pending_verification=pending_count,
    )


# API Design Notes for Interns:
#
# 1. Route Protection:
#    - All /api/ routes require authentication (Depends(get_current_user))
#    - HTML route (/farmservice) doesn't enforce auth server-side
#    - Frontend JavaScript handles auth check for HTML routes
#
# 2. Ownership Validation:
#    - Always verify user owns the resource before update/delete
#    - 403 Forbidden if user tries to access someone else's farm
#    - Security best practice: Never trust client-provided IDs
#
# 3. Error Handling:
#    - 400 Bad Request: Invalid input data (validation errors)
#    - 401 Unauthorized: No auth token or invalid token
#    - 403 Forbidden: Valid token but insufficient permissions
#    - 404 Not Found: Resource doesn't exist
#    - 500 Internal Server Error: Unexpected server errors
#
# 4. Database Transactions:
#    - commit(): Save changes to database
#    - rollback(): Undo changes on error
#    - refresh(): Reload object from database (get auto-generated values)
#
# 5. Calculated Fields:
#    - Area calculated from polygon coordinates
#    - Credits calculated from area and soil type
#    - Stored in database for performance (denormalization)
#    - Recalculated when relevant fields change
#
# 6. Response Models:
#    - response_model: FastAPI auto-validates and serializes output
#    - Ensures consistent API responses
#    - Auto-generates OpenAPI schema
#
# 7. Async/Await:
#    - All database operations are async (non-blocking)
#    - await: Wait for async operation to complete
#    - Better performance under load
