import logging
import logging.config
import os
from typing import Any, Dict

# Default logging configuration
DEFAULT_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
        "simple": {
            "format": "%(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "default",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
        "json_console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {  # Root logger
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "app": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


def get_logging_config() -> Dict[str, Any]:
    """
    Get logging configuration based on environment variables.

    Environment variables:
    - LOG_LEVEL: Set the root log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - LOG_FORMAT: Set the log format (default, json, simple)
    - LOG_HANDLERS: Set the handlers to use (console, file, json_console)
    - LOG_FILE: Set the log file path (default: logs/app.log)
    - LOG_MAX_BYTES: Set the max file size in bytes (default: 10485760)
    - LOG_BACKUP_COUNT: Set the number of backup files (default: 5)
    """
    config = DEFAULT_LOGGING_CONFIG.copy()

    # Get environment variables with defaults
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = os.getenv("LOG_FORMAT", "default")
    log_handlers = os.getenv("LOG_HANDLERS", "console").split(",")
    log_file = os.getenv("LOG_FILE", "logs/app.log")
    log_max_bytes = int(os.getenv("LOG_MAX_BYTES", "10485760"))
    log_backup_count = int(os.getenv("LOG_BACKUP_COUNT", "5"))

    # Validate log level
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if log_level not in valid_levels:
        log_level = "INFO"

    # Validate log format
    valid_formats = ["default", "json", "simple"]
    if log_format not in valid_formats:
        log_format = "default"

    # Validate handlers
    valid_handlers = ["console", "file", "json_console"]
    log_handlers = [
        h.strip() for h in log_handlers if h.strip() in valid_handlers
    ]
    if not log_handlers:
        log_handlers = ["console"]

    # Update configuration based on environment variables
    for logger_name in config["loggers"]:
        config["loggers"][logger_name]["level"] = log_level
        config["loggers"][logger_name]["handlers"] = log_handlers

    # Update file handler configuration
    if "file" in log_handlers:
        config["handlers"]["file"]["filename"] = log_file
        config["handlers"]["file"]["maxBytes"] = log_max_bytes
        config["handlers"]["file"]["backupCount"] = log_backup_count

        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except (OSError, PermissionError):
                # If we can't create the directory, remove file handler
                log_handlers.remove("file")
                for logger_name in config["loggers"]:
                    if "file" in config["loggers"][logger_name]["handlers"]:
                        config["loggers"][logger_name]["handlers"].remove(
                            "file"
                        )

    return config


def setup_logging() -> None:
    """Setup logging configuration."""
    try:
        config = get_logging_config()
        logging.config.dictConfig(config)
    except Exception:  # noqa: BLE001
        # Fallback to basic logging if configuration fails
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (defaults to 'app')

    Returns:
        Configured logger instance
    """
    if name is None:
        name = "app"
    return logging.getLogger(name)
