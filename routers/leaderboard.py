"""
Leaderboard Router

This module handles leaderboard-related endpoints:
- Get users ranked by points

Key Concepts for Interns:
- Sorting: ORDER BY in SQL
- Pagination: LIMIT and OFFSET for large datasets
- Query Parameters: Optional parameters in URL
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.user import User
from schemas.user import UserPublic

# Create router instance
router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get("", response_model=list[UserPublic])
async def get_leaderboard(
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of users to return"),
    offset: int = Query(default=0, ge=0, description="Number of users to skip"),
    db: AsyncSession = Depends(get_db)
) -> list[User]:
    """
    Get leaderboard of users sorted by points.
    
    This is a PUBLIC endpoint - no authentication required.
    Returns users sorted by points in descending order (highest first).
    
    Query Parameters:
        limit: Maximum number of users to return (1-1000, default 100)
        offset: Number of users to skip (for pagination, default 0)
        
    Args:
        limit: Maximum results (validated by Query)
        offset: Skip this many results (validated by Query)
        db: Database session (injected by dependency)
        
    Returns:
        list[User]: List of users sorted by points (descending)
        
    Example Request:
        GET /api/leaderboard?limit=10&offset=0
        
    Example Response (200 OK):
        [
            {
                "id": 5,
                "name": "Alice Smith",
                "username": "alice",
                "photo": "alice.jpg",
                "image_path": "/media/profile_pics/alice.jpg",
                "points": 500
            },
            {
                "id": 2,
                "name": "Bob Johnson",
                "username": "bob",
                "photo": null,
                "image_path": "/static/profile_pics/default.jpg",
                "points": 350
            },
            {
                "id": 1,
                "name": "John Doe",
                "username": "johndoe",
                "photo": null,
                "image_path": "/static/profile_pics/default.jpg",
                "points": 150
            }
        ]
        
    Pagination Example:
        - Page 1: GET /api/leaderboard?limit=10&offset=0
        - Page 2: GET /api/leaderboard?limit=10&offset=10
        - Page 3: GET /api/leaderboard?limit=10&offset=20
    """
    # Query users sorted by points (descending) with pagination
    result = await db.execute(
        select(User)
        .order_by(User.points.desc())  # Highest points first
        .limit(limit)  # Maximum number of results
        .offset(offset)  # Skip this many results
    )
    
    users = result.scalars().all()
    
    return users


# Best Practices for Interns:
#
# 1. Pagination:
#    - Always paginate large datasets to avoid performance issues
#    - Use limit (how many) and offset (skip how many)
#    - Set reasonable defaults and maximum limits
#    - Formula: page_number = (offset / limit) + 1
#
# 2. Query Parameters:
#    - Use Query() to add validation and documentation
#    - ge (greater than or equal), le (less than or equal)
#    - Provide default values for optional parameters
#    - Add descriptions for API documentation
#
# 3. Sorting:
#    - Use .order_by() for sorting
#    - .desc() for descending order (highest first)
#    - .asc() for ascending order (lowest first)
#    - Can sort by multiple columns: .order_by(User.points.desc(), User.name.asc())
#
# 4. Performance:
#    - Add database index on columns you sort by (we indexed 'points' in the model)
#    - Limit results to prevent loading entire table into memory
#    - Consider caching for frequently accessed data (future enhancement)
#
# 5. Future Enhancements:
#    - Add filtering (e.g., by date range, minimum points)
#    - Add search functionality
#    - Add total count for pagination UI
#    - Cache leaderboard results (Redis)
#    - Real-time updates (WebSockets)
