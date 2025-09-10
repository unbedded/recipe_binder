"""Recipe Binder utilities.

This module provides utility functions for file management, logging,
and other common operations used throughout the Recipe Binder pipeline.

Example usage:
    from recipe_fmt.utils import FileManager, setup_logging

    setup_logging(log_level="INFO")
    file_manager = FileManager()
"""

from .file_manager import FileManager
from .logging_setup import get_logger, log_exception, setup_logging

__all__ = ["FileManager", "setup_logging", "get_logger", "log_exception"]
