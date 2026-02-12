"""
Farm Pydantic Schemas

Schemas for validating farm data in API requests and responses.
These schemas enforce data validation, type checking, and API contracts.

Key Concepts:
- Request Schemas: Validate incoming data from clients
- Response Schemas: Format data sent to clients
- Field Validation: Ensure data meets requirements
- Type Safety: Catch errors before they reach the database
"""

from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


class FarmCreate(BaseModel):
    """
    Schema for creating a new farm.
    
    Used when a farmer registers a new farm through the API.
    Validates all required fields and ensures data quality.
    
    Fields:
        farm_name: Optional custom name
        phone: Farmer's contact (10 digits)
        district: Administrative district
        state: State/province
        soil_type: One of the valid soil types
        polygon_coordinates: Array of [lat, lon] points (min 3)
    """
    
    farm_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Custom name for the farm",
        examples=["Sunrise Acres", "Green Valley Farm"]
    )
    
    phone: str = Field(
        ...,
        min_length=10,
        max_length=15,
        description="Farmer's contact number",
        examples=["9876543210"]
    )
    
    district: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Administrative district",
        examples=["Pune", "Mumbai", "Bangalore"]
    )
    
    state: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="State or province",
        examples=["Maharashtra", "Karnataka", "Tamil Nadu"]
    )
    
    soil_type: Literal["Loamy", "Clay", "Sandy", "Mixed"] = Field(
        ...,
        description="Type of soil (affects carbon sequestration rate)"
    )
    
    polygon_coordinates: List[List[float]] = Field(
        ...,
        description="Array of [latitude, longitude] coordinate pairs defining farm boundary",
        examples=[
            [
                [18.5204, 73.8567],
                [18.5214, 73.8567],
                [18.5214, 73.8577],
                [18.5204, 73.8577]
            ]
        ]
    )
    
    @field_validator("polygon_coordinates")
    @classmethod
    def validate_polygon_coordinates(cls, v):
        """
        Validate polygon coordinates.
        
        Ensures:
        - At least 3 points (minimum for a polygon)
        - Each point has exactly 2 values [lat, lon]
        - Latitude in range [-90, 90]
        - Longitude in range [-180, 180]
        """
        if len(v) < 3:
            raise ValueError("Polygon must have at least 3 coordinate points")
        
        for i, coord in enumerate(v):
            if len(coord) != 2:
                raise ValueError(f"Coordinate {i} must have exactly 2 values [lat, lon]")
            
            lat, lon = coord
            
            if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
                raise ValueError(f"Coordinate {i} must contain numeric values")
            
            if not (-90 <= lat <= 90):
                raise ValueError(f"Invalid latitude at coordinate {i}: {lat}. Must be between -90 and 90")
            
            if not (-180 <= lon <= 180):
                raise ValueError(f"Invalid longitude at coordinate {i}: {lon}. Must be between -180 and 180")
        
        return v
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number contains only digits."""
        # Remove common separators
        cleaned = v.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        
        if not cleaned.isdigit():
            raise ValueError("Phone number must contain only digits")
        
        if len(cleaned) < 10:
            raise ValueError("Phone number must be at least 10 digits")
        
        return cleaned
    
    class Config:
        json_schema_extra = {
            "example": {
                "farm_name": "Sunrise Acres",
                "phone": "9876543210",
                "district": "Pune",
                "state": "Maharashtra",
                "soil_type": "Loamy",
                "polygon_coordinates": [
                    [18.5204, 73.8567],
                    [18.5214, 73.8567],
                    [18.5214, 73.8577],
                    [18.5204, 73.8577]
                ]
            }
        }


class FarmUpdate(BaseModel):
    """
    Schema for updating an existing farm.
    
    All fields are optional - only provided fields will be updated.
    Same validation rules as FarmCreate apply to provided fields.
    """
    
    farm_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    district: Optional[str] = Field(None, min_length=2, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=100)
    soil_type: Optional[Literal["Loamy", "Clay", "Sandy", "Mixed"]] = None
    polygon_coordinates: Optional[List[List[float]]] = None
    
    @field_validator("polygon_coordinates")
    @classmethod
    def validate_polygon_coordinates(cls, v):
        """Same validation as FarmCreate."""
        if v is None:
            return v
        
        if len(v) < 3:
            raise ValueError("Polygon must have at least 3 coordinate points")
        
        for i, coord in enumerate(v):
            if len(coord) != 2:
                raise ValueError(f"Coordinate {i} must have exactly 2 values [lat, lon]")
            
            lat, lon = coord
            
            if not (-90 <= lat <= 90):
                raise ValueError(f"Invalid latitude at coordinate {i}: {lat}")
            
            if not (-180 <= lon <= 180):
                raise ValueError(f"Invalid longitude at coordinate {i}: {lon}")
        
        return v
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        """Same validation as FarmCreate."""
        if v is None:
            return v
        
        cleaned = v.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        
        if not cleaned.isdigit():
            raise ValueError("Phone number must contain only digits")
        
        if len(cleaned) < 10:
            raise ValueError("Phone number must be at least 10 digits")
        
        return cleaned


class FarmResponse(BaseModel):
    """
    Schema for farm data in API responses.
    
    Returns complete farm information including calculated fields.
    Used when returning farm data to clients.
    """
    
    id: int
    farmer_id: int
    farm_name: Optional[str]
    phone: str
    latitude: float
    longitude: float
    area_hectares: float
    soil_type: str
    district: str
    state: str
    annual_credits: float
    annual_value_inr: float
    polygon_coordinates: List[List[float]]
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    display_name: str = Field(
        description="Display name (custom name or 'Farm #X')"
    )
    verification_status: str = Field(
        description="Human-readable verification status"
    )
    
    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models
        json_schema_extra = {
            "example": {
                "id": 1,
                "farmer_id": 123,
                "farm_name": "Sunrise Acres",
                "phone": "9876543210",
                "latitude": 18.5209,
                "longitude": 73.8572,
                "area_hectares": 3.2,
                "soil_type": "Loamy",
                "district": "Pune",
                "state": "Maharashtra",
                "annual_credits": 48.0,
                "annual_value_inr": 24000.0,
                "polygon_coordinates": [
                    [18.5204, 73.8567],
                    [18.5214, 73.8567],
                    [18.5214, 73.8577],
                    [18.5204, 73.8577]
                ],
                "is_verified": False,
                "created_at": "2026-02-12T10:30:00",
                "updated_at": "2026-02-12T10:30:00",
                "display_name": "Sunrise Acres",
                "verification_status": "Pending Verification"
            }
        }


class FarmStatistics(BaseModel):
    """
    Schema for aggregated farm statistics.
    
    Used in dashboard to display summary information
    about all farms owned by a farmer.
    """
    
    total_farms: int = Field(
        description="Total number of farms",
        ge=0
    )
    
    total_area_hectares: float = Field(
        description="Combined area of all farms in hectares",
        ge=0.0
    )
    
    total_annual_credits: float = Field(
        description="Total annual carbon credits across all farms",
        ge=0.0
    )
    
    total_annual_value_inr: float = Field(
        description="Total annual value in INR",
        ge=0.0
    )
    
    verified_farms: int = Field(
        description="Number of verified farms",
        ge=0
    )
    
    pending_verification: int = Field(
        description="Number of farms pending verification",
        ge=0
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_farms": 5,
                "total_area_hectares": 12.5,
                "total_annual_credits": 156.25,
                "total_annual_value_inr": 78125.0,
                "verified_farms": 3,
                "pending_verification": 2
            }
        }


class FarmListResponse(BaseModel):
    """
    Schema for listing farms with summary statistics.
    
    Combines individual farm data with aggregate statistics
    for efficient dashboard rendering.
    """
    
    summary: FarmStatistics
    farms: List[FarmResponse]
    
    class Config:
        json_schema_extra = {
            "example": {
                "summary": {
                    "total_farms": 2,
                    "total_area_hectares": 5.7,
                    "total_annual_credits": 71.25,
                    "total_annual_value_inr": 35625.0,
                    "verified_farms": 1,
                    "pending_verification": 1
                },
                "farms": [
                    {
                        "id": 1,
                        "farm_name": "Sunrise Acres",
                        "area_hectares": 3.2,
                        "annual_credits": 48.0,
                        "is_verified": True,
                        # ... other fields
                    }
                ]
            }
        }


# Schema Design Notes for Interns:
#
# 1. Request vs Response Schemas:
#    - Request (Create/Update): Only fields the client provides
#    - Response: All fields including auto-generated ones (id, timestamps, calculated fields)
#    - Separation ensures clear API contracts
#
# 2. Field Validation:
#    - @field_validator: Custom validation logic
#    - Field(...): Built-in constraints (min_length, max_length, ge, le)
#    - Literal: Restricts to specific values (enum-like)
#
# 3. Optional vs Required:
#    - Required: Field(...) with ellipsis
#    - Optional: Optional[type] = None or Field(None)
#    - Update schemas typically have all optional fields
#
# 4. ORM Mode (from_attributes):
#    - Allows creating Pydantic models from SQLAlchemy objects
#    - Pydantic will call object.field_name to get values
#    - Essential for database → API response conversion
#
# 5. Examples:
#    - json_schema_extra provides API documentation examples
#    - Shown in auto-generated Swagger/ReDoc
#    - Helps frontend developers understand data structure
#
# 6. Validation Flow:
#    - Client sends JSON → FastAPI deserializes → Pydantic validates
#    - If validation fails: 422 error with detailed message
#    - If validation succeeds: Proceed to route handler
#
# 7. Type Safety:
#    - Pydantic enforces types at runtime
#    - IDEs can provide autocomplete/type checking
#    - Reduces bugs from incorrect data types
