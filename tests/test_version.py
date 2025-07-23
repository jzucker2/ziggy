"""
Tests for the version module.
"""

from app.version import __app_description__, __app_name__, __version__


class TestVersion:
    """Test version information."""

    def test_version_attributes(self):
        """Test that version attributes are defined correctly."""
        assert __version__ == "1.0.0"
        assert __app_name__ == "Ziggy"
        assert __app_description__ == "Zigbee2MQTT Prometheus Metrics Exporter"

    def test_version_format(self):
        """Test that version follows semantic versioning format."""
        # Version should be in format X.Y.Z
        version_parts = __version__.split(".")
        assert len(version_parts) == 3
        assert all(part.isdigit() for part in version_parts)

    def test_app_name_not_empty(self):
        """Test that app name is not empty."""
        assert __app_name__ is not None
        assert len(__app_name__) > 0

    def test_app_description_not_empty(self):
        """Test that app description is not empty."""
        assert __app_description__ is not None
        assert len(__app_description__) > 0
