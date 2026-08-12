"""
Infrastructure Layer - Configuration

Centralized configuration management using Pydantic Settings.
Supports environment variables via .env files.

Features:
- Type-safe configuration
- Environment variable support
- Automatic directory creation
- Validation on load
"""

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration using Pydantic Settings.

    Configuration priority (highest to lowest):
    1. Environment variables
    2. .env file
    3. Default values

    Attributes:
        PROJECT_ROOT: Root directory of the project
        DATA_DIR: Main data directory
        RAW_DIR: Raw data directory
        PROCESSED_DIR: Processed data directory
        EMBEDDINGS_DIR: Word embeddings directory
        LOGS_DIR: Application logs directory
        DATABASE_URL: Database connection URL
        LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        LOG_FILE: Log file path
        BATCH_SIZE: Batch size for data processing
        MIN_WORD_LENGTH: Minimum word length to process
        MAX_WORD_LENGTH: Maximum word length to process
        SCHEMA_VERSION: Current database schema version

    Examples:
        >>> settings = Settings()
        >>> settings.DATABASE_URL
        'sqlite:///data/swahili_knowledge.db'
        >>> settings.BATCH_SIZE
        1000
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra fields from .env
    )

    # ==================== DIRECTORIES ====================

    PROJECT_ROOT: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent,
        description="Project root directory",
    )

    DATA_DIR: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent / "data",
        description="Main data directory",
    )

    RAW_DIR: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent / "data" / "raw",
        description="Raw data directory",
    )

    PROCESSED_DIR: Path = Field(
        default_factory=lambda: (
            Path(__file__).parent.parent.parent / "data" / "processed"
        ),
        description="Processed data directory",
    )

    EMBEDDINGS_DIR: Path = Field(
        default_factory=lambda: (
            Path(__file__).parent.parent.parent / "data" / "embeddings"
        ),
        description="Embeddings directory",
    )

    LOGS_DIR: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent / "data" / "logs",
        description="Logs directory",
    )

    # ==================== DATABASE ====================

    DATABASE_URL: str = Field(
        default="sqlite:///data/swahili_knowledge.db",
        description="Database connection URL",
    )

    DB_ECHO: bool = Field(
        default=False, description="Echo SQL statements (for debugging)"
    )

    DB_POOL_SIZE: int = Field(
        default=5, ge=1, le=20, description="Database connection pool size"
    )

    DB_MAX_OVERFLOW: int = Field(
        default=10, ge=0, le=50, description="Maximum overflow connections"
    )

    # ==================== DATA FILES ====================

    MASAKHANE_POS_FILE: Path = Field(
        default_factory=lambda: (
            Path(__file__).parent.parent.parent
            / "data"
            / "raw"
            / "masakhane-pos"
            / "pos_swa_test.txt"
        ),
        description="Masakhane POS data file",
    )

    MASAKHANE_NER_FILE: Path = Field(
        default_factory=lambda: (
            Path(__file__).parent.parent.parent
            / "data"
            / "raw"
            / "masakhane-ner"
            / "ner_swa_test.txt"
        ),
        description="Masakhane NER data file",
    )

    MASAKHANE_NEWS_FILE: Path = Field(
        default_factory=lambda: (
            Path(__file__).parent.parent.parent
            / "data"
            / "raw"
            / "masakhane-news"
            / "news_swa_test.tsv"
        ),
        description="Masakhane News data file",
    )

    KAMUSI_CSV_FILE: Path = Field(
        default_factory=lambda: (
            Path(__file__).parent.parent.parent
            / "data"
            / "raw"
            / "kamusi"
            / "words.csv"
        ),
        description="Kamusi dictionary CSV file",
    )

    KAMUSI_JSON_FILE: Path = Field(
        default_factory=lambda: (
            Path(__file__).parent.parent.parent
            / "data"
            / "raw"
            / "kamusi"
            / "words.json"
        ),
        description="Kamusi dictionary JSON file",
    )

    # ==================== LOGGING ====================

    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    LOG_FILE: Path | None = Field(
        default_factory=lambda: (
            Path(__file__).parent.parent.parent / "data" / "logs" / "app.log"
        ),
        description="Log file path (None for console only)",
    )

    LOG_ROTATION: str = Field(default="10 MB", description="Log file rotation size")

    LOG_RETENTION: str = Field(
        default="1 week", description="Log file retention period"
    )

    LOG_COMPRESSION: str = Field(
        default="zip", description="Log file compression format"
    )

    # ==================== PROCESSING ====================

    BATCH_SIZE: int = Field(
        default=1000, ge=1, le=10000, description="Batch size for data processing"
    )

    MIN_WORD_LENGTH: int = Field(
        default=2, ge=1, le=10, description="Minimum word length to process"
    )

    MAX_WORD_LENGTH: int = Field(
        default=50, ge=10, le=200, description="Maximum word length to process"
    )

    NUM_WORKERS: int = Field(
        default=4, ge=1, le=16, description="Number of worker processes"
    )

    # ==================== APPLICATION ====================

    APP_NAME: str = Field(
        default="Swahili Linguistic Intelligence API", description="Application name"
    )

    ENVIRONMENT: str = Field(
        default="development",
        description="Environment (development, staging, production)",
    )

    DEBUG: bool = Field(
        default=True, description="Debug mode (do not use in production!)"
    )

    SCHEMA_VERSION: str = Field(default="0.2.0", description="Database schema version")

    # ==================== VALIDATORS ====================

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v_upper

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment."""
        valid_envs = {"development", "staging", "production"}
        v_lower = v.lower()
        if v_lower not in valid_envs:
            raise ValueError(f"Invalid environment: {v}. Must be one of {valid_envs}")
        return v_lower

    # ==================== METHODS ====================

    def setup_directories(self) -> None:
        """
        Create necessary directories if they don't exist.

        Creates:
            - DATA_DIR
            - RAW_DIR
            - PROCESSED_DIR
            - EMBEDDINGS_DIR
            - LOGS_DIR
        """
        for directory in [
            self.DATA_DIR,
            self.RAW_DIR,
            self.PROCESSED_DIR,
            self.EMBEDDINGS_DIR,
            self.LOGS_DIR,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"

    def get_database_path(self) -> Path | None:
        """
        Get database file path if using SQLite.

        Returns:
            Path to database file if SQLite, None otherwise
        """
        if self.DATABASE_URL.startswith("sqlite:///"):
            db_path = self.DATABASE_URL.replace("sqlite:///", "")
            return Path(db_path)
        return None

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Settings("
            f"env={self.ENVIRONMENT}, "
            f"db={self.DATABASE_URL}, "
            f"log_level={self.LOG_LEVEL}"
            f")"
        )


# Singleton instance
settings = Settings()

# Ensure directories exist on import
settings.setup_directories()


# Convenience functions
def get_settings() -> Settings:
    """
    Get the singleton settings instance.

    Returns:
        Settings instance
    """
    return settings


def reload_settings() -> Settings:
    """
    Reload settings from environment.

    Useful after changing .env file.

    Returns:
        New Settings instance
    """
    global settings
    settings = Settings()
    settings.setup_directories()
    return settings


# Usage example
if __name__ == "__main__":
    print("=== Configuration Settings ===\n")

    # Display main settings
    print(f"App Name: {settings.APP_NAME}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug Mode: {settings.DEBUG}")
    print(f"Schema Version: {settings.SCHEMA_VERSION}")

    print("\n--- Directories ---")
    print(f"Project Root: {settings.PROJECT_ROOT}")
    print(f"Data Directory: {settings.DATA_DIR}")
    print(f"Raw Data: {settings.RAW_DIR}")
    print(f"Logs: {settings.LOGS_DIR}")

    print("\n--- Database ---")
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"Pool Size: {settings.DB_POOL_SIZE}")
    print(f"Echo SQL: {settings.DB_ECHO}")

    print("\n--- Processing ---")
    print(f"Batch Size: {settings.BATCH_SIZE}")
    print(f"Min Word Length: {settings.MIN_WORD_LENGTH}")
    print(f"Max Word Length: {settings.MAX_WORD_LENGTH}")

    print("\n--- Logging ---")
    print(f"Log Level: {settings.LOG_LEVEL}")
    print(f"Log File: {settings.LOG_FILE}")

    print("\n--- Environment Checks ---")
    print(f"Is Production: {settings.is_production()}")
    print(f"Is Development: {settings.is_development()}")

    # Test directory creation
    print("\n--- Testing Directory Creation ---")
    settings.setup_directories()
    print("✓ All directories created/verified")
