import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.version import __version__

client = TestClient(app)


class TestRootEndpoint:
    """Test cases for the root endpoint."""

    def test_root_endpoint(self):
        """Test that the root endpoint returns the expected welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Welcome to Ziggy API"
        assert data["version"] == __version__
        assert data["status"] == "running"

    def test_root_endpoint_content_type(self):
        """Test that the root endpoint returns JSON content type."""
        response = client.get("/")
        assert response.headers["content-type"] == "application/json"


class TestHealthEndpoint:
    """Test cases for the health endpoint."""

    def test_health_endpoint(self):
        """Test that the health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "environment" in data
        assert "platform" in data
        assert "python" in data
        assert "mqtt" in data

    def test_health_endpoint_content_type(self):
        """Test that the health endpoint returns JSON content type."""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"

    def test_health_endpoint_timestamp_format(self):
        """Test that the timestamp is a valid number."""
        response = client.get("/health")
        data = response.json()

        # Check that timestamp is a valid number (Unix timestamp)
        timestamp = data["timestamp"]
        assert isinstance(timestamp, (int, float))
        assert timestamp > 0

    def test_health_endpoint_environment_default(self):
        """Test that the environment defaults to development."""
        response = client.get("/health")
        data = response.json()
        assert data["environment"] == "development"

    def test_health_endpoint_platform_info(self):
        """Test that platform information is included."""
        response = client.get("/health")
        data = response.json()

        platform_info = data["platform"]
        assert isinstance(platform_info, dict)
        assert "system" in platform_info
        assert "release" in platform_info
        assert "version" in platform_info

    def test_health_endpoint_python_version(self):
        """Test that Python version is included."""
        response = client.get("/health")
        data = response.json()

        python_info = data["python"]
        assert isinstance(python_info, dict)
        assert "version" in python_info
        assert "implementation" in python_info

    def test_health_endpoint_response_structure(self):
        """Test that the health response has the expected structure."""
        response = client.get("/health")
        data = response.json()

        expected_keys = {
            "status",
            "timestamp",
            "environment",
            "platform",
            "python",
            "mqtt",
        }
        actual_keys = set(data.keys())
        assert expected_keys == actual_keys


class TestMetricsEndpoint:
    """Test cases for the metrics endpoint."""

    def test_metrics_endpoint_exists(self):
        """Test that the metrics endpoint exists and returns 200."""
        response = client.get("/metrics")
        assert response.status_code == 200

    @pytest.mark.skip(
        reason="Prometheus metrics may not be available in test environment"
    )
    def test_metrics_endpoint_contains_prometheus_data(self):
        """Test that the metrics endpoint contains Prometheus-formatted data."""
        response = client.get("/metrics")
        content = response.text

        # Check for basic Prometheus metrics format
        assert "# HELP" in content or "# TYPE" in content


class TestAppConfiguration:
    """Test cases for FastAPI app configuration."""

    def test_app_title(self):
        """Test that the app has the correct title."""
        assert app.title == "Ziggy API"

    def test_app_description(self):
        """Test that the app has the correct description."""
        assert (
            app.description
            == "A FastAPI application for Zigbee device management with MQTT integration"
        )

    def test_app_version(self):
        """Test that the app has the correct version."""
        assert app.version == __version__

    def test_app_docs_endpoint(self):
        """Test that the docs endpoint is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_app_openapi_endpoint(self):
        """Test that the OpenAPI endpoint is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200


class TestErrorHandling:
    """Test cases for error handling."""

    def test_404_endpoint(self):
        """Test that 404 errors are handled properly."""
        response = client.get("/nonexistent")
        assert response.status_code == 404

        data = response.json()
        assert "error" in data
        assert data["error"] == "Not found"

    def test_method_not_allowed(self):
        """Test that method not allowed errors are handled properly."""
        response = client.post("/health")
        assert response.status_code == 405

        data = response.json()
        assert "error" in data
        assert data["error"] == "Method not allowed"

    def test_health_post_method(self):
        """Test that POST to health endpoint returns 405."""
        response = client.post("/health")
        assert response.status_code == 405


class TestResponseHeaders:
    """Test cases for response headers."""

    def test_cors_headers_not_present(self):
        """Test that CORS headers are not present by default."""
        response = client.get("/")
        assert "access-control-allow-origin" not in response.headers

    def test_content_type_header(self):
        """Test that content-type header is set correctly."""
        response = client.get("/")
        assert response.headers["content-type"] == "application/json"


class TestMQTTEndpoints:
    """Test cases for MQTT-related endpoints."""

    def test_mqtt_status_endpoint(self):
        """Test that the MQTT status endpoint exists."""
        response = client.get("/mqtt/status")
        assert response.status_code == 200

        data = response.json()
        assert "enabled" in data

        # Check structure based on enabled state
        if data["enabled"]:
            assert "connected" in data
            assert "connection_info" in data
        else:
            assert "message" in data

    def test_mqtt_metrics_endpoint(self):
        """Test that the MQTT metrics endpoint exists."""
        response = client.get("/mqtt/metrics")
        assert response.status_code == 200

        data = response.json()
        assert "enabled" in data

        # Check structure based on enabled state
        if data["enabled"]:
            assert "metrics_info" in data
        else:
            assert "message" in data

    def test_zigbee2mqtt_metrics_endpoint(self):
        """Test that the Zigbee2MQTT metrics endpoint exists."""
        response = client.get("/zigbee2mqtt/metrics")
        assert response.status_code == 200

        data = response.json()
        assert "enabled" in data

        # Check structure based on enabled state
        if data["enabled"]:
            assert "metrics_info" in data
        else:
            assert "message" in data
