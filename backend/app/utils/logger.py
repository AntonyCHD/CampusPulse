"""Logger utility."""

import sys
from pathlib import Path

from loguru import logger

from backend.app.config import get_settings


def setup_logger():
    """Setup logger configuration."""
    settings = get_settings()

    # Remove default handler
    logger.remove()

    # Console handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=settings.log_level,
    )

    # File handler
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        settings.log_file,
        rotation="100 MB",
        retention="7 days",
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
    )

    return logger


def get_logger(name: str = __name__):
    """Get a logger instance for the given module name."""
    return log.bind(name=name)


# Global logger instance
log = setup_logger()
