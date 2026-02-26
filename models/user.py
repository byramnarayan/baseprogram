"""
User Database Model

This module defines the User model - the database table structure for users.
It uses SQLAlchemy ORM to map Python objects to database rows.

Key Concepts for Interns:
- ORM (Object-Relational Mapping): Work with database using Python objects
- Table Columns: Define the structure of your database table
- Indexes: Speed up database queries on specific columns
- Properties: Computed values that aren't stored in the database
"""

from datetime import datetime

from sqlalchemy import Index, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    """
    User Model - Represents a user in the system.
    
    This class defines the structure of the 'users' table in the database.
    Each instance of this class represents one row in the table.
    
    Attributes:
        id: Unique identifier for the user (primary key)
        name: User's full name
        username: Unique username for login and display
        email: Unique email address for login
        phone: Contact phone number
        address: Optional physical address
        photo: Filename of profile picture (optional)
        password_hash: Hashed password (NEVER store plain text!)
        points: Gamification points for leaderboard
        created_at: Timestamp when user was created
        
    Properties:
        image_path: Full path to profile picture (computed property)
    """
    
    # Table name in the database
    __tablename__ = "users"
    
    # Primary Key - Unique identifier for each user
    # auto_increment means the database automatically assigns the next number
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # User Information Fields
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(15), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Profile Picture - stores filename only, not the actual image
    photo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Security - NEVER store plain text passwords!
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # Gamification
    points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Metadata - Track when user was created
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    # Indexes for better query performance
    # Composite index for common queries
    __table_args__ = (
        Index('idx_user_email_lower', 'email'),  # Case-insensitive email lookup
        Index('idx_user_username_lower', 'username'),  # Case-insensitive username lookup
    )
    
    # Relationship with Farm model
    farms: Mapped[list["Farm"]] = relationship(  # type: ignore
        "Farm",
        back_populates="owner",
        cascade="all, delete-orphan",  # Delete farms when user is deleted
    )

    # Relationship with Conversation model (AI Help)
    conversations: Mapped[list["Conversation"]] = relationship(  # type: ignore
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Plant Discovery relationships
    plant_discoveries: Mapped[list["PlantDiscovery"]] = relationship(  # type: ignore
        "PlantDiscovery",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    daily_streaks: Mapped[list["DailyStreak"]] = relationship(  # type: ignore
        "DailyStreak",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    user_tree: Mapped["UserTree | None"] = relationship(  # type: ignore
        "UserTree",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    
    @property
    def image_path(self) -> str:
        """
        Get the full path to the user's profile picture.
        
        This is a computed property - it's not stored in the database,
        but calculated on-the-fly when accessed.
        
        Returns:
            str: Path to profile picture or default image
            
        Example:
            >>> user = User(photo="abc123.jpg")
            >>> print(user.image_path)
            '/media/profile_pics/abc123.jpg'
            
            >>> user2 = User(photo=None)
            >>> print(user2.image_path)
            '/static/profile_pics/default.jpg'
        """
        if self.photo:
            return f"/media/profile_pics/{self.photo}"
        return "/static/profile_pics/default.jpg"
    
    def __repr__(self) -> str:
        """
        String representation of the User object.
        
        This is useful for debugging - when you print a User object,
        you'll see a readable representation instead of just the memory address.
        
        Returns:
            str: String representation of the user
            
        Example:
            >>> user = User(id=1, username="john_doe")
            >>> print(user)
            <User(id=1, username='john_doe')>
        """
        return f"<User(id={self.id}, username='{self.username}')>"


# Database Design Notes for Interns:
# 
# 1. Primary Keys: Every table should have a primary key (unique identifier)
# 2. Indexes: Add indexes on columns you'll frequently search/filter by
#    - username and email are indexed because we search by them during login
#    - Indexes speed up reads but slow down writes (trade-off to consider)
# 3. Unique Constraints: username and email must be unique (no duplicates)
# 4. Nullable Fields: address and photo are optional (nullable=True)
# 5. Data Types: Choose appropriate types (String, Integer, Text, DateTime)
# 6. Defaults: points defaults to 0, created_at defaults to current time
# 7. Security: NEVER store passwords in plain text - always hash them!
