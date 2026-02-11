"""
User Schemas

Pydantic models for user-related requests and responses.
These schemas define what data is accepted and returned by the API.

Key Concepts for Interns:
- Request Validation: Ensure incoming data is valid before processing
- Response Serialization: Control what data is sent back to clients
- Data Privacy: Different schemas for public vs private data
- Field Validation: Min/max lengths, email format, etc.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """
    Base User Schema
    
    Contains common fields shared across multiple user schemas.
    This follows the DRY (Don't Repeat Yourself) principle.
    
    Attributes:
        name: User's full name (1-100 characters)
        username: Unique username (1-50 characters)
        email: Valid email address
        phone: Phone number (1-15 characters)
        address: Optional physical address
    """
    name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    username: str = Field(..., min_length=1, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="Valid email address")
    phone: str = Field(..., min_length=1, max_length=15, description="Contact phone number")
    address: str | None = Field(None, description="Physical address (optional)")


class UserCreate(UserBase):
    """
    User Creation Schema
    
    Used when registering a new user. Extends UserBase with password field.
    
    Attributes:
        password: Plain text password (min 8 characters)
        
    Note: Password is validated here, then hashed before storing in database.
    
    Example Request:
        {
            "name": "John Doe",
            "username": "johndoe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "address": "123 Main St",
            "password": "SecurePass123"
        }
    """
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")


class UserPublic(BaseModel):
    """
    Public User Schema
    
    Used when displaying user information to OTHER users.
    Does NOT include sensitive information like email or phone.
    
    This is what you see on someone else's profile or in the leaderboard.
    
    Attributes:
        id: User's unique identifier
        name: User's full name
        username: Username
        photo: Profile picture filename (optional)
        image_path: Full path to profile picture
        points: User's points for leaderboard
        
    Example Response:
        {
            "id": 1,
            "name": "John Doe",
            "username": "johndoe",
            "photo": "abc123.jpg",
            "image_path": "/media/profile_pics/abc123.jpg",
            "points": 150
        }
    """
    model_config = ConfigDict(from_attributes=True)  # Allow creation from ORM models
    
    id: int
    name: str
    username: str
    photo: str | None
    image_path: str  # Computed from photo field
    points: int


class UserPrivate(UserPublic):
    """
    Private User Schema
    
    Used when displaying user information to the USER THEMSELVES.
    Includes all public fields PLUS sensitive information.
    
    This is what you see on your own profile/dashboard.
    
    Attributes:
        email: User's email address
        phone: User's phone number
        address: User's address (optional)
        
    Example Response:
        {
            "id": 1,
            "name": "John Doe",
            "username": "johndoe",
            "photo": "abc123.jpg",
            "image_path": "/media/profile_pics/abc123.jpg",
            "points": 150,
            "email": "john@example.com",
            "phone": "+1234567890",
            "address": "123 Main St"
        }
    """
    email: EmailStr
    phone: str
    address: str | None


class UserUpdate(BaseModel):
    """
    User Update Schema
    
    Used when updating user information. All fields are optional.
    Only include fields you want to update.
    
    Attributes:
        name: New name (optional)
        username: New username (optional)
        photo: New profile picture filename (optional)
        
    Example Request (update only name):
        {
            "name": "Jane Doe"
        }
        
    Example Request (update multiple fields):
        {
            "name": "Jane Doe",
            "username": "janedoe",
            "photo": "newphoto.jpg"
        }
    """
    name: str | None = Field(None, min_length=1, max_length=100)
    username: str | None = Field(None, min_length=1, max_length=50)
    photo: str | None = None


# Schema Design Patterns for Interns:
#
# 1. Separation of Concerns:
#    - UserCreate: What data is needed to create a user
#    - UserPublic: What data is safe to show to everyone
#    - UserPrivate: What data only the user themselves should see
#    - UserUpdate: What data can be modified
#
# 2. Field Validation:
#    - Use Field() to add constraints (min_length, max_length, etc.)
#    - EmailStr automatically validates email format
#    - Optional fields use "| None" type hint
#
# 3. Privacy by Design:
#    - Never expose sensitive data (email, phone) in public schemas
#    - Use different schemas for different contexts
#    - Password is NEVER returned in any response schema
#
# 4. from_attributes=True:
#    - Allows Pydantic to create schemas from SQLAlchemy models
#    - Without this, you'd have to manually convert ORM objects to dicts
