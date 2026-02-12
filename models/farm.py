"""
Farm Database Model

This module defines the Farm model for storing farm records with geospatial data.
Each farm belongs to a user (farmer) and contains location, area, soil type,
and calculated carbon credit information.

Key Features:
- Geospatial data storage (coordinates, polygons, area)
- Relationship with User model (farmer ownership)
- Automatic carbon credit calculations
- Verification workflow support
"""

from datetime import datetime
from typing import List

from sqlalchemy import (
    Index,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Farm(Base):
    """
    Farm Model - Represents a farm with geospatial and carbon credit data.
    
    This model stores individual farm records including location data,
    physical characteristics (area, soil type), and calculated carbon credits.
    
    Attributes:
        id: Unique identifier for the farm (primary key)
        farmer_id: Foreign key to User who owns this farm
        farm_name: Optional custom name for the farm
        phone: Farmer's contact number for this farm
        latitude: Center latitude coordinate
        longitude: Center longitude coordinate
        area_hectares: Total farm area in hectares (calculated from polygon)
        soil_type: Type of soil (affects carbon sequestration)
        district: Administrative district location
        state: State/province location
        annual_credits: Calculated annual carbon credits
        annual_value_inr: Monetary value of credits in INR
        polygon_coordinates: JSON array of [lat, lon] boundary points
        is_verified: Whether farm is verified by validator
        created_at: When farm was registered
        updated_at: Last modification timestamp
        
    Relationships:
        owner: User who owns this farm (many-to-one)
    """
    
    # Table name in the database
    __tablename__ = "farms"
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign Key - Links to User model
    farmer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),  # Delete farms when user is deleted
        nullable=False,
        index=True,  # Index for fast queries by farmer
    )
    
    # Farm Basic Information
    farm_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        default=None,
    )
    
    phone: Mapped[str] = mapped_column(String(15), nullable=False)
    
    # Geospatial Data
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    area_hectares: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Agricultural Data
    soil_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        # Valid values: "Loamy", "Clay", "Sandy", "Mixed"
    )
    
    # Location Data
    district: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Carbon Credit Calculations
    annual_credits: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    annual_value_inr: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    # Geospatial Polygon
    # Stores array of [lat, lon] coordinates as JSON
    # Example: [[18.52, 73.85], [18.53, 73.85], [18.53, 73.86]]
    polygon_coordinates: Mapped[List] = mapped_column(JSON, nullable=False)
    
    # Verification Status
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    
    # Relationship with User model
    owner: Mapped["User"] = relationship(  # type: ignore
        "User",
        back_populates="farms",
    )
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_farmer_verified", "farmer_id", "is_verified"),  # Common query
        Index("idx_location", "latitude", "longitude"),  # Spatial queries
        Index("idx_district_state", "district", "state"),  # Location filtering
    )
    
    @property
    def display_name(self) -> str:
        """
        Get display name for the farm.
        
        Returns custom farm name if set, otherwise generates default name
        based on farm ID.
        
        Returns:
            str: Display name for the farm
            
        Example:
            >>> farm = Farm(id=1, farm_name="Sunrise Acres")
            >>> print(farm.display_name)
            'Sunrise Acres'
            
            >>> farm2 = Farm(id=2, farm_name=None)
            >>> print(farm2.display_name)
            'Farm #2'
        """
        if self.farm_name:
            return self.farm_name
        return f"Farm #{self.id}"
    
    @property
    def verification_status(self) -> str:
        """
        Get human-readable verification status.
        
        Returns:
            str: "Verified" or "Pending Verification"
        """
        return "Verified" if self.is_verified else "Pending Verification"
    
    def __repr__(self) -> str:
        """
        String representation of the Farm object.
        
        Returns:
            str: String representation
            
        Example:
            >>> farm = Farm(id=1, display_name="Sunrise Acres", area_hectares=3.2)
            >>> print(farm)
            <Farm(id=1, name='Sunrise Acres', area=3.2ha)>
        """
        return (
            f"<Farm(id={self.id}, name='{self.display_name}', "
            f"area={self.area_hectares}ha)>"
        )


# Database Design Notes:
#
# 1. Foreign Key Relationship:
#    - farmer_id links to users.id
#    - CASCADE delete: When user is deleted, their farms are also deleted
#    - This maintains referential integrity
#
# 2. Geospatial Data Storage:
#    - polygon_coordinates stored as JSON (flexible, works with SQLite)
#    - For production with PostgreSQL, could use PostGIS geometry type
#    - latitude/longitude stored separately for quick map centering
#
# 3. Calculated Fields:
#    - annual_credits and annual_value_inr are denormalized (stored)
#    - Alternative: Calculate on-the-fly (slower but always accurate)
#    - Trade-off: Storage space vs computation time
#
# 4. Verification System:
#    - is_verified flag enables approval workflow
#    - Unverified farms get 50% credits (calculated in carbon_calculator)
#    - Future: Add verified_by foreign key to track who verified
#
# 5. Indexing Strategy:
#    - farmer_id: Fast lookups for "show all my farms"
#    - (farmer_id, is_verified): Fast filtering by verification status
#    - (latitude, longitude): Future spatial queries
#    - (district, state): Location-based filtering/analytics
#
# 6. JSON Column:
#    - SQLite supports JSON natively (as of SQLite 3.38+)
#    - Can query/filter JSON data using JSON functions
#    - Stores array of coordinates efficiently
#
# 7. Auto-updating Timestamps:
#    - created_at: Set once on creation
#    - updated_at: Automatically updates on any change (onupdate)
#    - Useful for auditing and tracking changes
