import os
import platform
import sys
from unittest.mock import patch

from app.app_metrics import get_app_info, update_app_info
from app.version import __app_description__, __app_name__, __version__


class TestAppMetrics:
    """Test app metrics functionality."""

    def test_app_constants(self):
        """Test that app constants are defined correctly."""
        assert (
            __version__ == __version__
        )  # This will always pass, but we're testing the import
        assert __app_name__ == "Ziggy"
        assert __app_description__ == "Zigbee2MQTT Prometheus Metrics Exporter"

    def test_get_app_info(self):
        """Test getting application information."""
        app_info = get_app_info()

        # Check required fields
        assert "version" in app_info
        assert "name" in app_info
        assert "description" in app_info
        assert "python_version" in app_info
        assert "python_implementation" in app_info
        assert "platform" in app_info
        assert "environment" in app_info

        # Check values
        assert app_info["version"] == __version__
        assert app_info["name"] == __app_name__
        assert app_info["description"] == __app_description__
        assert app_info["python_version"] == sys.version
        assert (
            app_info["python_implementation"]
            == platform.python_implementation()
        )

        # Check platform info
        platform_info = app_info["platform"]
        assert "system" in platform_info
        assert "release" in platform_info
        assert "version" in platform_info
        assert "machine" in platform_info
        assert "processor" in platform_info

        # Check environment info
        env_info = app_info["environment"]
        assert "environment" in env_info
        assert "log_level" in env_info

    def test_get_app_info_with_environment_variables(self):
        """Test getting app info with environment variables set."""
        with patch.dict(
            os.environ, {"ENVIRONMENT": "test", "LOG_LEVEL": "DEBUG"}
        ):
            app_info = get_app_info()
            env_info = app_info["environment"]
            assert env_info["environment"] == "test"
            assert env_info["log_level"] == "DEBUG"

    def test_get_app_info_without_environment_variables(self):
        """Test getting app info without environment variables set."""
        with patch.dict(os.environ, {}, clear=True):
            app_info = get_app_info()
            env_info = app_info["environment"]
            assert env_info["environment"] == "development"
            assert env_info["log_level"] == "info"

    def test_update_app_info(self):
        """Test updating application information metrics."""
        app_info = {
            "version": __version__,
            "name": "Test App",
            "description": "Test Description",
            "python_version": "3.13.0",
            "python_implementation": "CPython",
            "platform": {
                "system": "Linux",
                "release": "5.4.0",
                "version": "test version",
                "machine": "x86_64",
                "processor": "Intel",
            },
            "environment": {
                "environment": "test",
                "log_level": "DEBUG",
            },
        }

        # This should not raise any exceptions
        update_app_info(app_info)

    def test_update_app_info_with_nested_data(self):
        """Test updating application information with nested data structures."""
        app_info = {
            "version": __version__,
            "nested_data": {
                "key1": "value1",
                "key2": "value2",
            },
            "simple_data": "simple_value",
        }

        # This should not raise any exceptions
        update_app_info(app_info)

    def test_update_app_info_with_complex_data(self):
        """Test updating app info with complex data types."""
        app_info = {
            "version": __version__,
            "numbers": {
                "int_value": 42,
                "float_value": 3.14,
            },
            "booleans": {
                "true_value": True,
                "false_value": False,
            },
            "none_value": None,
        }

        # This should not raise any exceptions
        update_app_info(app_info)
