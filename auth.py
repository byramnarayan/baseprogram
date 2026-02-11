"""
Authentication and Security Module

This module handles all authentication-related functionality:
- Password hashing and verification
- JWT token creation and validation
- User authentication dependency for protected routes

Key Concepts for Interns:
- Password Hashing: Never store plain text passwords!
- JWT (JSON Web Tokens): Stateless authentication tokens
- OAuth2: Industry-standard authorization framework
- Dependency Injection: FastAPI's way of sharing code between routes
"""

from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db

# Password hashing setup using Argon2 (industry-standard, secure algorithm)
# Argon2 is recommended over bcrypt for new applications

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)
# OAuth2 scheme for token-based authentication
# This tells FastAPI where to look for the token (in the Authorization header)
# tokenUrl is the endpoint where users can get a token (login endpoint)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")


# def hash_password(password: str) -> str:
#     """
#     Hash a plain text password using Argon2.
    
#     This function takes a plain text password and returns a secure hash.
#     The hash is what gets stored in the database - NEVER the plain password!
    
#     Args:
#         password: Plain text password from user input
        
#     Returns:
#         str: Hashed password safe for database storage
        
#     Example:
#         >>> hashed = hash_password("mySecurePassword123")
#         >>> print(hashed)
#         '$argon2id$v=19$m=65536,t=3,p=4$...'
#     """
#     return pwd_context.hash(password)


# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """
#     Verify a plain text password against a hashed password.
    
#     This is used during login to check if the provided password matches
#     the stored hash in the database.
    
#     Args:
#         plain_password: Password provided by user during login
#         hashed_password: Hashed password from database
        
#     Returns:
#         bool: True if password matches, False otherwise
        
#     Example:
#         >>> hashed = hash_password("myPassword")
#         >>> verify_password("myPassword", hashed)
#         True
#         >>> verify_password("wrongPassword", hashed)
#         False
#     """
#     return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.
    
    JWT tokens are used for stateless authentication. The token contains
    user information (claims) and is signed with a secret key.
    
    Args:
        data: Dictionary of claims to include in the token (e.g., {"sub": "user_id"})
        expires_delta: How long the token should be valid (optional)
        
    Returns:
        str: Encoded JWT token
        
    Token Structure:
        - Header: Algorithm and token type
        - Payload: User data (claims) and expiration
        - Signature: Ensures token hasn't been tampered with
        
    Example:
        >>> token = create_access_token({"sub": "123"})
        >>> print(token)
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    """
    # Create a copy of the data to avoid modifying the original
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default to configured expiration time
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    # Add expiration claim to token
    to_encode.update({"exp": expire})
    
    # Encode and sign the token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key.get_secret_value(),  # Secret key for signing
        algorithm=settings.algorithm,  # HS256 algorithm
    )
    
    return encoded_jwt


def verify_access_token(token: str) -> str | None:
    """
    Verify and decode a JWT access token.
    
    This function checks if a token is valid and hasn't expired.
    If valid, it returns the user ID from the token.
    
    Args:
        token: JWT token to verify
        
    Returns:
        str | None: User ID if token is valid, None otherwise
        
    Example:
        >>> token = create_access_token({"sub": "123"})
        >>> user_id = verify_access_token(token)
        >>> print(user_id)
        '123'
    """
    try:
        # Decode and verify the token
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
        )
        
        # Extract user ID from the "sub" (subject) claim
        user_id: str = payload.get("sub")
        
        if user_id is None:
            return None
            
        return user_id
        
    except JWTError:
        # Token is invalid or expired
        return None


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db),
):
    """
    Dependency to get the current authenticated user.
    
    This is a FastAPI dependency that:
    1. Extracts the JWT token from the Authorization header
    2. Verifies the token is valid
    3. Fetches the user from the database
    4. Returns the user object
    
    This dependency is used in protected routes to ensure only
    authenticated users can access them.
    
    Args:
        token: JWT token from Authorization header (injected by oauth2_scheme)
        db: Database session (injected by get_db dependency)
        
    Returns:
        User: The authenticated user object
        
    Raises:
        HTTPException: 401 Unauthorized if token is invalid or user not found
        
    Usage in routes:
        @app.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user": current_user.username}
    """
    # Import here to avoid circular imports
    from models.user import User
    
    # Define the exception to raise if authentication fails
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify the token and extract user ID
    user_id = verify_access_token(token)
    
    if user_id is None:
        raise credentials_exception
    
    # Fetch user from database
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user


# Type alias for easier use in route handlers
# Instead of writing "current_user: User = Depends(get_current_user)" every time,
# you can write "current_user: CurrentUser"
CurrentUser = Annotated[object, Depends(get_current_user)]

# Example usage in a route:
# @app.get("/me")
# async def read_users_me(current_user: CurrentUser):
#     return current_user
