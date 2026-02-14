"""
Centralized logging configuration for UPI Mule Detection Backend.
Provides production-grade logging with proper error tracking.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Configure root logger
logger = logging.getLogger("upi_mule_detection")
logger.setLevel(logging.INFO)

# Remove any existing handlers to avoid duplicates
logger.handlers.clear()

# Format for log messages
log_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# File handler with rotation (10MB per file, keep 5 backups)
file_handler = RotatingFileHandler(
    LOGS_DIR / "app.log",
    maxBytes=10_485_760,  # 10 MB
    backupCount=5
)
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)

# Console handler for development/debugging
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_format)
logger.addHandler(console_handler)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module."""
    return logging.getLogger(f"upi_mule_detection.{name}")
