"""
Users Router

This module handles user-related endpoints:
- Get current user profile
- Update current user
- Delete current user
- View any user's public profile

Key Concepts for Interns:
- Protected Routes: Require authentication via Depends(get_current_user)
- Authorization: Ensuring users can only modify their own data
- CRUD Operations: Create, Read, Update, Delete
- Response Models: Control what data is returned
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from database import get_db
from models.user import User
from schemas.user import UserPrivate, UserPublic, UserUpdate

# Create router instance
router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserPrivate)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user's profile.
    
    This is a protected endpoint - requires authentication.
    Returns the full profile of the authenticated user (including private data).
    
    Args:
        current_user: Authenticated user (injected by get_current_user dependency)
        
    Returns:
        User: Current user's full profile
        
    Example Request:
        GET /api/users/me
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        
    Example Response (200 OK):
        {
            "id": 1,
            "name": "John Doe",
            "username": "johndoe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "address": "123 Main St",
            "photo": null,
            "image_path": "/static/profile_pics/default.jpg",
            "points": 150
        }
    """
    return current_user


@router.patch("/me", response_model=UserPrivate)
async def update_current_user(
    name: str = Form(None),
    username: str = Form(None),
    photo: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Update current user's profile.
    
    This is a protected endpoint - requires authentication.
    Users can only update their own profile.
    
    Updatable fields:
    - name
    - username (must be unique)
    - photo (file upload)
    
    Args:
        name: New name (optional)
        username: New username (optional)
        photo: Profile picture file (optional)
        current_user: Authenticated user (injected by dependency)
        db: Database session (injected by dependency)
        
    Returns:
        User: Updated user profile
        
    Raises:
        HTTPException 400: If new username is already taken or file is invalid
    """
    import os
    import uuid
    from pathlib import Path
    
    # If username is being updated, check if it's already taken
    if username and username != current_user.username:
        result = await db.execute(
            select(User).where(User.username.ilike(username))
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Update name if provided
    if name:
        current_user.name = name
    
    # Update username if provided
    if username:
        current_user.username = username
    
    # Handle photo upload
    if photo and photo.filename:
        # Validate file type
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
        file_ext = Path(photo.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only JPG, PNG, and GIF are allowed."
            )
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        
        # Create media directory if it doesn't exist
        media_dir = Path("media/profile_pics")
        media_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = media_dir / unique_filename
        with open(file_path, "wb") as f:
            content = await photo.read()
            f.write(content)
        
        # Update user photo field
        current_user.photo = unique_filename
    
    # Save changes
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete current user's account.
    
    This is a protected endpoint - requires authentication.
    Permanently deletes the user's account and all associated data.
    
    WARNING: This action cannot be undone!
    
    Args:
        current_user: Authenticated user (injected by dependency)
        db: Database session (injected by dependency)
        
    Returns:
        204 No Content: Account deleted successfully
        
    Example Request:
        DELETE /api/users/me
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        
    Example Response:
        204 No Content
    """
    # Delete the user
    await db.delete(current_user)
    await db.commit()
    
    # Return 204 No Content (no response body)
    return None


@router.get("/{user_id}", response_model=UserPublic)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get a user's public profile by ID.
    
    This is a PUBLIC endpoint - no authentication required.
    Returns only public information (no email, phone, or address).
    
    Args:
        user_id: ID of the user to retrieve
        db: Database session (injected by dependency)
        
    Returns:
        User: User's public profile
        
    Raises:
        HTTPException 404: If user not found
        
    Example Request:
        GET /api/users/123
        
    Example Response (200 OK):
        {
            "id": 123,
            "name": "John Doe",
            "username": "johndoe",
            "photo": "abc123.jpg",
            "image_path": "/media/profile_pics/abc123.jpg",
            "points": 150
        }
    """
    # Find user by ID
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    # Return 404 if user not found
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


# Best Practices for Interns:
#
# 1. Authentication vs Authorization:
#    - Authentication: Who are you? (handled by get_current_user)
#    - Authorization: What can you do? (checked in route logic)
#    - Example: Everyone can view profiles (no auth), but only you can edit yours (auth + ownership check)
#
# 2. PATCH vs PUT:
#    - PATCH: Partial update (only send fields you want to change)
#    - PUT: Full replacement (must send all fields)
#    - We use PATCH because it's more flexible
#
# 3. Response Models:
#    - UserPrivate: For the user's own data (includes email, phone)
#    - UserPublic: For other users' data (no sensitive info)
#    - This is privacy by design!
#
# 4. Database Updates:
#    - Use model_dump(exclude_unset=True) to only update provided fields
#    - Use setattr() to dynamically set attributes
#    - Always commit() and refresh() after changes
#
# 5. Error Handling:
#    - 404 Not Found: Resource doesn't exist
#    - 400 Bad Request: Invalid input (e.g., username taken)
#    - 401 Unauthorized: Not authenticated
#    - 403 Forbidden: Authenticated but not allowed (not used here, but important)
