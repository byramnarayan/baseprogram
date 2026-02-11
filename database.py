"""
Database Configuration Module

This module sets up the async SQLAlchemy engine and session management.
It provides the foundation for all database operations in the application.

Key Concepts for Interns:
- Async/Await: Non-blocking database operations for better performance
- SQLAlchemy ORM: Object-Relational Mapping - work with Python objects instead of SQL
- Session Management: Handles database connections and transactions
- Dependency Injection: FastAPI's way of providing database sessions to routes
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


# Database URL - using async SQLite for development
# For production, switch to PostgreSQL:
# SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./app.db"

# Create async engine
# The engine is the starting point for any SQLAlchemy application
# It manages the connection pool and provides a source of database connectivity
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite
    echo=False,  # Set to True to see SQL queries in console (useful for debugging)
)

# Create async session factory
# A session is a workspace for your database operations
# It tracks changes and manages transactions
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit (allows access outside session)
    autocommit=False,  # Transactions must be explicitly committed
    autoflush=False,  # Don't automatically flush changes to database
)


# Base class for all database models
# All your SQLAlchemy models should inherit from this class
class Base(DeclarativeBase):
    """
    Base class for all database models.
    
    This uses SQLAlchemy 2.0's declarative base system.
    All models inherit from this class to get ORM functionality.
    """
    pass


# Dependency function for FastAPI routes
# This function provides a database session to route handlers
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Database Session Dependency
    
    This is a FastAPI dependency that provides a database session to routes.
    It automatically handles session creation and cleanup.
    
    Usage in routes:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            # Use db session here
            pass
    
    Yields:
        AsyncSession: An async database session
        
    How it works:
    1. Creates a new session when a request comes in
    2. Yields the session to the route handler
    3. Automatically closes the session when the request is done
    4. Ensures proper cleanup even if an error occurs
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Example of creating tables (called in main.py during startup)
async def create_tables():
    """
    Create all database tables.
    
    This function creates all tables defined by models that inherit from Base.
    It should be called during application startup.
    """
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


# Example of dropping tables (useful for development/testing)
async def drop_tables():
    """
    Drop all database tables.
    
    WARNING: This deletes all data! Only use in development/testing.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
