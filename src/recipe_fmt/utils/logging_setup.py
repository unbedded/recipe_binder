"""Centralized logging configuration for Recipe Binder.

This module provides thread-safe logging setup following CLAUDE.md standards
with file output, timestamps, and appropriate logging levels.

Example usage:
    from recipe_fmt.utils.logging_setup import setup_logging

    # Basic setup
    setup_logging()

    # Custom configuration
    setup_logging(
        log_level="DEBUG",
        log_file="custom.log",
        console_output=True
    )
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Any


def setup_logging(
    log_level: str = "WARNING",
    log_file: str | None = None,
    console_output: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> logging.Logger:
    """Setup comprehensive logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Log file path. If None, uses default based on caller
        console_output: Whether to output to console/stderr
        max_file_size: Maximum log file size in bytes before rotation
        backup_count: Number of backup log files to keep

    Returns:
        Configured root logger
    """
    # STEP_1: Validate log level
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if log_level.upper() not in valid_levels:
        raise ValueError(f"Invalid log level: {log_level}. Must be one of: {valid_levels}")

    # STEP_2: Determine log file path
    if log_file is None:
        log_file = "recipe_binder.log"

    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # STEP_3: Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Clear any existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # STEP_4: Create formatter with timestamps and thread info
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(threadName)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # STEP_5: Setup file handler with rotation
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_file_size, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    except Exception as e:
        # If file logging fails, at least continue with console logging
        print(f"Warning: Failed to setup file logging: {e}")

    # STEP_6: Setup console handler if requested
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # STEP_7: Log initial configuration
    root_logger.info("Logging configured - Level: %s, File: %s, Console: %s", log_level, log_file, console_output)

    return root_logger


def get_logger(name: str, cfg_dict: dict[str, Any] | None = None) -> logging.Logger:
    """Get a configured logger following CLAUDE.md standards.

    This function ensures logging is instantiated as the first step
    in constructors and follows proper configuration management.

    Args:
        name: Logger name (typically __name__)
        cfg_dict: Configuration dictionary with logging settings

    Returns:
        Configured logger instance
    """
    # STEP_8: Apply configuration defaults
    config = _apply_logging_config_defaults(cfg_dict or {})

    # STEP_9: Setup logging if not already configured
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        setup_logging(
            log_level=config.get("log_level", "WARNING"),
            log_file=config.get("log_file"),
            console_output=config.get("console_output", True),
        )

    # STEP_10: Return named logger
    logger = logging.getLogger(name)

    # Configure lazy formatting for performance
    logger._log_with_lazy_formatting = True

    return logger


def _apply_logging_config_defaults(cfg_dict: dict) -> dict:
    """Apply logging configuration defaults.

    Args:
        cfg_dict: Input configuration dictionary

    Returns:
        Configuration with defaults applied
    """
    defaults = {
        "log_level": "WARNING",
        "log_file": None,
        "console_output": True,
        "max_file_size": 10 * 1024 * 1024,  # 10MB
        "backup_count": 5,
        "thread_safe": True,
    }

    for key, default_value in defaults.items():
        if key not in cfg_dict:
            cfg_dict[key] = default_value

    return cfg_dict


class ThreadSafeFileHandler(logging.handlers.RotatingFileHandler):
    """Thread-safe rotating file handler with proper locking.

    This handler ensures thread safety as required by CLAUDE.md standards.
    """

    def __init__(self, *args, **kwargs):
        """Initialize thread-safe file handler."""
        super().__init__(*args, **kwargs)
        # Use a lock for thread safety
        self.lock = logging._lock

    def emit(self, record):
        """Emit a log record with thread safety."""
        try:
            with self.lock:
                super().emit(record)
        except Exception:
            self.handleError(record)


def setup_module_logging(module_name: str, cfg_dict: dict = None) -> logging.Logger:
    """Setup logging for a specific module following CLAUDE.md patterns.

    This function should be called as the first step in module constructors.

    Args:
        module_name: Name of the module (typically __name__)
        cfg_dict: Configuration dictionary

    Returns:
        Configured logger for the module
    """
    # STEP_11: Get module logger
    logger = get_logger(module_name, cfg_dict)

    # STEP_12: Log module initialization
    logger.debug("Module logging initialized: %s", module_name)

    # STEP_13: Demonstrate key operation logging
    logger.info("Module %s ready for operation", module_name)

    return logger


def log_exception(logger: logging.Logger, message: str, exception: Exception = None):
    """Log exceptions with stack traces as per CLAUDE.md standards.

    Args:
        logger: Logger instance
        message: Descriptive error message
        exception: Exception to log (if None, logs current exception)
    """
    if exception:
        logger.exception("%s: %s", message, str(exception))
    else:
        logger.exception(message)


def configure_third_party_loggers():
    """Configure third-party library loggers to avoid noise.

    This reduces logging from external libraries that might be too verbose.
    """
    # Reduce noise from common third-party libraries
    noisy_loggers = [
        "urllib3.connectionpool",
        "requests.packages.urllib3",
        "openai",
        "httpx",
        "httpcore",
    ]

    for logger_name in noisy_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING)


# STEP_14: Demonstrate logging usage patterns
def demonstrate_logging_patterns():
    """Demonstrate proper logging patterns from CLAUDE.md.

    This function shows examples of proper logging usage.
    """
    logger = get_logger(__name__)

    # Input validation logging
    logger.debug("Validating input parameters")

    # Cache access logging
    logger.debug("Accessing cache for key: %s", "example_key")

    # Calculation steps logging
    logger.info("Starting calculation with parameters: %s", {"param1": "value1"})

    # Error logging with stack trace
    try:
        # Simulated operation
        pass
    except Exception as e:
        log_exception(logger, "Operation failed", e)

    # Avoid logging sensitive information
    # GOOD: logger.info("User login successful for user ID: %s", user_id)
    # BAD:  logger.info("User login with password: %s", password)

    # Use lazy formatting for performance
    logger.debug("Processing %d items with config %s", 100, {"setting": "value"})


if __name__ == "__main__":
    # Example usage and testing
    setup_logging(log_level="DEBUG", log_file="test_logging.log")
    demonstrate_logging_patterns()
    print("Logging demonstration complete - check test_logging.log")
