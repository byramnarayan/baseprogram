"""
Configuration Management Module

This module uses Pydantic Settings to manage application configuration.
It automatically loads values from environment variables and .env files.

Key Concepts for Interns:
- Pydantic Settings: Type-safe configuration management
- Environment Variables: Secure way to store sensitive data
- SecretStr: Prevents accidental logging of sensitive values
- Default Values: Fallback values if environment variables aren't set
"""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings

    This class defines all configuration variables for the application.
    Values are automatically loaded from:
    1. Environment variables (highest priority)
    2. .env file (if it exists)
    3. Default values defined here (lowest priority)

    Attributes:
        secret_key: Secret key for JWT token signing (MUST be kept secret!)
        algorithm: Algorithm used for JWT encoding/decoding
        access_token_expire_minutes: How long JWT tokens remain valid
        app_name: Application name for display purposes
        debug: Enable debug mode (should be False in production)
    """

    # Model configuration - tells Pydantic where to find environment variables
    model_config = SettingsConfigDict(
        env_file=".env",  # Load from .env file
        env_file_encoding="utf-8",  # Use UTF-8 encoding
        case_sensitive=False,
        extra="ignore",  # Environment variables are case-insensitive
    )

    # Security Settings
    secret_key: SecretStr  # Required - no default for security
    algorithm: str = "HS256"  # HMAC with SHA-256
    access_token_expire_minutes: int = 60  # 1 hour token lifetime

    # Application Settings
    app_name: str = "FastAPI User Management"
    debug: bool = False  # Always False in production!

    # Neo4j Settings
    neo4j_uri: str
    neo4j_username: str
    neo4j_password: str
    neo4j_database: str
    aura_instanceid: str
    aura_instancename: str
    gemini_api_key: str
    sarvam_api_key: str
    sarvam_base_url: str = "https://api.sarvam.ai"

    # Qdrant
    qdrant_enabled: bool = False  # set true only if Qdrant + embedding endpoint are available
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "farm_knowledge"
    qdrant_top_k: int = 5

    # mem0
    mem0_api_key: str = ""  # empty = local in-memory mode

    # PlantNet
    plantnet_api_key: str = "your_plantnet_api_key_here"
    plantnet_base_url: str = "https://my-api.plantnet.org/v2"


# Create a single instance to be imported throughout the application
# This follows the Singleton pattern - one configuration object for the entire app
settings = Settings()

# Example usage in other modules:
# from config import settings
# print(settings.app_name)
# secret = settings.secret_key.get_secret_value()  # Access the actual secret value
