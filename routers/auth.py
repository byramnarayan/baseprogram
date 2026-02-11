"""
Authentication Router

This module handles all authentication-related endpoints:
- User registration
- User login (token generation)

Key Concepts for Interns:
- APIRouter: Organizes related endpoints into modules
- OAuth2PasswordRequestForm: Standard form for username/password login
- Status Codes: HTTP status codes communicate the result of requests
- Error Handling: Proper error responses for different scenarios
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import create_access_token, hash_password, verify_password
from config import settings
from database import get_db
from models.user import User
from schemas.auth import Token
from schemas.user import UserCreate, UserPrivate

# Create router instance
# prefix="/api/auth" means all routes here will start with /api/auth
# tags=["auth"] groups these endpoints in the API documentation
router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Register a new user.
    
    This endpoint creates a new user account with the provided information.
    
    Process:
    1. Validate input data (Pydantic does this automatically)
    2. Check if username or email already exists
    3. Hash the password (NEVER store plain text!)
    4. Create user in database
    5. Return user information (without password!)
    
    Args:
        user_data: User registration data (validated by Pydantic)
        db: Database session (injected by FastAPI)
        
    Returns:
        User: The newly created user object
        
    Raises:
        HTTPException 400: If username or email already exists
        
    Example Request:
        POST /api/auth/register
        {
            "name": "John Doe",
            "username": "johndoe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "address": "123 Main St",
            "password": "SecurePass123"
        }
        
    Example Response (201 Created):
        {
            "id": 1,
            "name": "John Doe",
            "username": "johndoe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "address": "123 Main St",
            "photo": null,
            "image_path": "/static/profile_pics/default.jpg",
            "points": 0
        }
    """
    # Check if username already exists (case-insensitive)
    result = await db.execute(
        select(User).where(User.username.ilike(user_data.username))
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists (case-insensitive)
    result = await db.execute(
        select(User).where(User.email.ilike(user_data.email))
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user object
    # Note: We hash the password before storing it!
    new_user = User(
        name=user_data.name,
        username=user_data.username,
        email=user_data.email.lower(),  # Store email in lowercase for consistency
        phone=user_data.phone,
        address=user_data.address,
        password_hash=hash_password(user_data.password),  # Hash the password!
        points=0,  # New users start with 0 points
    )
    
    # Add to database
    db.add(new_user)
    await db.commit()  # Save changes to database
    await db.refresh(new_user)  # Refresh to get the auto-generated ID
    
    return new_user


@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Login and get access token.
    
    This endpoint authenticates a user and returns a JWT token.
    The token is used for subsequent authenticated requests.
    
    Process:
    1. Find user by email (username field contains email)
    2. Verify password matches stored hash
    3. Create JWT token with user ID
    4. Return token to client
    
    Args:
        form_data: OAuth2 form with username (email) and password
        db: Database session (injected by FastAPI)
        
    Returns:
        dict: Access token and token type
        
    Raises:
        HTTPException 401: If credentials are invalid
        
    Example Request:
        POST /api/auth/token
        Content-Type: application/x-www-form-urlencoded
        
        username=john@example.com&password=SecurePass123
        
    Example Response (200 OK):
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
        
    Note: OAuth2PasswordRequestForm uses "username" field, but we accept email there.
    This is a common pattern - the field name is "username" but it can contain email.
    """
    # Find user by email (case-insensitive)
    # form_data.username actually contains the email
    result = await db.execute(
        select(User).where(User.email.ilike(form_data.username))
    )
    user = result.scalar_one_or_none()
    
    # Check if user exists and password is correct
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    # The "sub" (subject) claim contains the user ID
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    # Return token in OAuth2 format
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# Logout endpoint (optional - logout is typically handled client-side)
@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout():
    """
    Logout endpoint.
    
    Note: With JWT tokens, logout is typically handled client-side by
    deleting the token from storage (localStorage, cookies, etc.).
    
    This endpoint exists for consistency and can be extended to:
    - Blacklist tokens (requires Redis or similar)
    - Log logout events
    - Clear server-side sessions (if using them)
    
    Returns:
        204 No Content: Logout successful
    """
    # In a JWT-based system, the client just deletes the token
    # No server-side action needed for basic implementation
    return None


# Best Practices for Interns:
#
# 1. Status Codes:
#    - 200 OK: Successful GET/POST/PATCH
#    - 201 Created: Successful resource creation
#    - 204 No Content: Successful DELETE or action with no response
#    - 400 Bad Request: Invalid input data
#    - 401 Unauthorized: Authentication failed
#    - 403 Forbidden: Authenticated but not authorized
#    - 404 Not Found: Resource doesn't exist
#    - 500 Internal Server Error: Server error
#
# 2. Security:
#    - Always hash passwords before storing
#    - Use case-insensitive email/username lookups
#    - Return generic error messages (don't reveal if email exists)
#    - Use HTTPS in production
#    - Set appropriate token expiration times
#
# 3. Database Operations:
#    - Always use async/await with async database sessions
#    - Commit changes with await db.commit()
#    - Refresh objects after commit to get auto-generated fields
#    - Use select() for queries, not raw SQL
#
# 4. Error Handling:
#    - Raise HTTPException for expected errors
#    - Let FastAPI handle unexpected errors
#    - Provide clear, user-friendly error messages
#    - Include appropriate status codes
