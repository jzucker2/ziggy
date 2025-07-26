import logging
import os
import platform
import sys
from typing import Any, Dict

from prometheus_client import Info

from app.version import __app_description__, __app_name__, __version__

logger = logging.getLogger(__name__)

# Application Info Metric
ziggy_app_info = Info(
    "ziggy_app_info",
    "Ziggy application information",
    labelnames=["app_name", "bridge_name"],
)

# Application version and metadata
APP_VERSION = __version__
APP_NAME = __app_name__
APP_DESCRIPTION = __app_description__


def get_app_info() -> Dict[str, Any]:
    """Collect application information for metrics."""
    return {
        "version": APP_VERSION,
        "name": APP_NAME,
        "description": APP_DESCRIPTION,
        "python_version": sys.version,
        "python_implementation": platform.python_implementation(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "environment": {
            "environment": os.getenv("ENVIRONMENT", "development"),
            "log_level": os.getenv("LOG_LEVEL", "info"),
        },
    }


def update_app_info(app_info: Dict[str, Any], bridge_name: str = "default"):
    """Update application information metrics."""
    # Flatten nested data for Prometheus compatibility
    flattened_info = {}
    for key, value in app_info.items():
        if isinstance(value, dict):
            # Flatten nested dictionaries
            for nested_key, nested_value in value.items():
                flattened_info[f"{key}_{nested_key}"] = str(nested_value)
        else:
            flattened_info[key] = str(value)

    # Update the application info metric
    ziggy_app_info.labels(app_name="ziggy", bridge_name=bridge_name).info(
        flattened_info
    )

    logger.debug(
        f"Updated application info metrics - keys: {list(app_info.keys())}, bridge_name: {bridge_name}"
    )
