"""
Utility functions for the web exploratory testing framework.
Provides common functionality for timestamping, file naming, text sanitization, and logging.
"""

import re
import os
from datetime import datetime
from typing import Optional
import logging


def get_timestamp(format_string: str = "%Y-%m-%d_%H-%M-%S") -> str:
    """
    Generate a formatted timestamp string.

    Args:
        format_string: DateTime format string (default: YYYY-MM-DD_HH-MM-SS)

    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime(format_string)


def get_iso_timestamp() -> str:
    """
    Generate an ISO 8601 formatted timestamp.

    Returns:
        ISO formatted timestamp string
    """
    return datetime.now().isoformat()


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    Sanitize a string to be safe for use as a filename.

    Args:
        filename: Original filename string
        max_length: Maximum length of the sanitized filename

    Returns:
        Sanitized filename string
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', filename)

    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(' .')

    # Replace multiple spaces/underscores with single underscore
    sanitized = re.sub(r'[_\s]+', '_', sanitized)

    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized or "unnamed"


def sanitize_text(text: str, max_length: int = 200) -> str:
    """
    Sanitize text for use in logs and reports.

    Args:
        text: Original text
        max_length: Maximum length of sanitized text

    Returns:
        Sanitized text string
    """
    # Remove excessive whitespace
    sanitized = re.sub(r'\s+', ' ', text.strip())

    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."

    return sanitized


def ensure_directory(directory_path: str) -> str:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        directory_path: Path to the directory

    Returns:
        Absolute path to the directory
    """
    abs_path = os.path.abspath(directory_path)
    os.makedirs(abs_path, exist_ok=True)
    return abs_path


def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    """
    Set up a logger with both file and console handlers.

    Args:
        name: Logger name
        log_file: Path to log file
        level: Logging level

    Returns:
        Configured logger instance
    """
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir:
        ensure_directory(log_dir)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '[%(levelname)s] %(message)s'
    )

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger


def format_duration(seconds: float) -> str:
    """
    Format a duration in seconds to a human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string (e.g., "2m 30s", "1h 5m 12s")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)


def truncate_url(url: str, max_length: int = 80) -> str:
    """
    Truncate a URL for display purposes.

    Args:
        url: Full URL
        max_length: Maximum length

    Returns:
        Truncated URL with ellipsis if needed
    """
    if len(url) <= max_length:
        return url
    return url[:max_length - 3] + "..."


def extract_domain(url: str) -> str:
    """
    Extract domain from a URL.

    Args:
        url: Full URL

    Returns:
        Domain name
    """
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return parsed.netloc or "unknown"


def is_same_domain(url1: str, url2: str) -> bool:
    """
    Check if two URLs are from the same domain.

    Args:
        url1: First URL
        url2: Second URL

    Returns:
        True if same domain, False otherwise
    """
    return extract_domain(url1) == extract_domain(url2)


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes.

    Args:
        file_path: Path to file

    Returns:
        File size in MB
    """
    if not os.path.exists(file_path):
        return 0.0
    return os.path.getsize(file_path) / (1024 * 1024)
