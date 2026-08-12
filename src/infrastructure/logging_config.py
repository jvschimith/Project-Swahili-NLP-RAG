"""
Infrastructure Layer - Logging Configuration

Structured logging setup using Loguru.

Features:
- Console and file logging
- Log rotation
- Colored output for console
- Structured format
- Multiple log levels
"""

import sys
from pathlib import Path

from loguru import logger


def setup_logging(
    log_level: str = "INFO",
    log_file: Path | None = None,
    rotation: str = "10 MB",
    retention: str = "1 week",
    compression: str = "zip",
    colorize: bool = True,
) -> None:
    """
    Configure application logging with Loguru.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (None for console only)
        rotation: When to rotate log file (size or time)
        retention: How long to keep old log files
        compression: Compression format for old logs
        colorize: Enable colors in console output

    Examples:
        >>> setup_logging("DEBUG", Path("logs/app.log"))
        >>> logger.info("Application started")
        >>> logger.error("An error occurred")
    """
    # Remove default handler
    logger.remove()

    # Console handler with colors
    logger.add(
        sys.stderr,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        level=log_level,
        colorize=colorize,
        backtrace=True,
        diagnose=True,
    )

    # File handler with rotation (if file provided)
    if log_file:
        # Ensure parent directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            str(log_file),
            format=(
                "{time:YYYY-MM-DD HH:mm:ss} | "
                "{level: <8} | "
                "{name}:{function}:{line} - "
                "{message}"
            ),
            level=log_level,
            rotation=rotation,
            retention=retention,
            compression=compression,
            backtrace=True,
            diagnose=True,
        )

        logger.info(f"Logging to file: {log_file}")

    logger.info(f"Logging initialized at {log_level} level")


def get_logger(name: str = None):
    """
    Get a logger instance.

    Args:
        name: Logger name (optional)

    Returns:
        Logger instance

    Examples:
        >>> log = get_logger(__name__)
        >>> log.info("Starting process")
    """
    if name:
        return logger.bind(name=name)
    return logger


# Usage example
if __name__ == "__main__":
    # Setup logging
    setup_logging(log_level="DEBUG", log_file=Path("test.log"), colorize=True)

    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.success("This is a success message")

    # Test with context
    logger.info("Processing {count} items", count=100)

    # Test exception logging
    try:
        result = 1 / 0
    except Exception:
        logger.exception("An error occurred")

    print("\n✓ Logging test complete! Check test.log")
