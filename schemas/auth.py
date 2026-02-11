"""
Authentication Schemas

Pydantic models for authentication-related requests and responses.

Key Concepts for Interns:
- Pydantic: Data validation using Python type hints
- Schemas: Define the structure of API requests and responses
- Validation: Automatic validation of incoming data
"""

from pydantic import BaseModel


class Token(BaseModel):
    """
    Token Response Schema
    
    This is what the login endpoint returns when authentication is successful.
    
    Attributes:
        access_token: The JWT token string
        token_type: Type of token (always "bearer" for JWT)
        
    Example Response:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Token Payload Schema
    
    This represents the data stored inside a JWT token.
    Used internally for token validation.
    
    Attributes:
        user_id: ID of the authenticated user (optional during validation)
        
    Note: The "sub" (subject) claim in JWT typically contains the user ID
    """
    user_id: int | None = None
