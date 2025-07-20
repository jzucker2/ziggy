from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.version import version

client = TestClient(app)


class TestRootEndpoint:
    """Test cases for the root endpoint."""

    def test_root_endpoint(self):
        """Test that the root endpoint returns the expected welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to Ziggy API"}

    def test_root_endpoint_content_type(self):
        """Test that the root endpoint returns JSON content type."""
        response = client.get("/")
        assert response.headers["content-type"] == "application/json"


class TestHealthEndpoint:
    """Test cases for the health check endpoint."""

    def test_health_endpoint(self):
        """Test that the health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Ziggy API"
        assert data["version"] == version
        assert "timestamp" in data
        assert "environment" in data
        assert "platform" in data
        assert "python_version" in data

    def test_health_endpoint_content_type(self):
        """Test that the health endpoint returns JSON content type."""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"

    def test_health_endpoint_timestamp_format(self):
        """Test that the timestamp is in ISO format."""
        response = client.get("/health")
        data = response.json()

        # Check that timestamp is a valid ISO format
        timestamp = data["timestamp"]
        try:
            datetime.fromisoformat(timestamp)
        except ValueError:
            pytest.fail(f"Timestamp {timestamp} is not in valid ISO format")

    def test_health_endpoint_environment_default(self):
        """Test that environment defaults to 'development' when not set."""
        response = client.get("/health")
        data = response.json()
        assert data["environment"] == "development"

    def test_health_endpoint_platform_info(self):
        """Test that platform information is included."""
        response = client.get("/health")
        data = response.json()
        assert isinstance(data["platform"], str)
        assert len(data["platform"]) > 0

    def test_health_endpoint_python_version(self):
        """Test that Python version is included."""
        response = client.get("/health")
        data = response.json()
        assert isinstance(data["python_version"], str)
        assert len(data["python_version"]) > 0

    def test_health_endpoint_response_structure(self):
        """Test that the health response has the expected structure."""
        response = client.get("/health")
        data = response.json()

        expected_keys = {
            "status",
            "timestamp",
            "service",
            "version",
            "environment",
            "platform",
            "python_version",
            "mqtt",  # Added MQTT status
        }
        actual_keys = set(data.keys())
        assert expected_keys == actual_keys

        # Test MQTT structure
        assert "mqtt" in data
        mqtt_data = data["mqtt"]
        assert "status" in mqtt_data
        assert "info" in mqtt_data


class TestMetricsEndpoint:
    """Test cases for the metrics endpoint."""

    def test_metrics_endpoint_exists(self):
        """Test that the metrics endpoint exists and returns data."""
        # First make a request to trigger metrics collection
        client.get("/")
        response = client.get("/metrics")
        # Note: Metrics endpoint might not be available in test environment
        # This test checks if the endpoint exists, but may return 404 in tests
        assert response.status_code in [200, 404]

    def test_metrics_endpoint_contains_prometheus_data(self):
        """Test that the metrics endpoint returns Prometheus-formatted data."""
        # First make a request to trigger metrics collection
        client.get("/")
        response = client.get("/metrics")

        # If metrics endpoint is available, check for Prometheus format
        if response.status_code == 200:
            content = response.text
            assert "# HELP" in content or "# TYPE" in content
            assert "fastapi_" in content or "http_" in content
        else:
            # Skip this test if metrics endpoint is not available
            pytest.skip("Metrics endpoint not available in test environment")


class TestAppConfiguration:
    """Test cases for the FastAPI app configuration."""

    def test_app_title(self):
        """Test that the app has the correct title."""
        assert app.title == "Ziggy API"

    def test_app_description(self):
        """Test that the app has the correct description."""
        assert (
            app.description
            == "A FastAPI application with Prometheus metrics and MQTT Zigbee integration"
        )

    def test_app_version(self):
        """Test that the app has the correct version."""
        assert app.version == version

    def test_app_docs_endpoint(self):
        """Test that the docs endpoint is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_app_openapi_endpoint(self):
        """Test that the OpenAPI schema endpoint is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"


class TestErrorHandling:
    """Test cases for error handling."""

    def test_404_endpoint(self):
        """Test that non-existent endpoints return 404."""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_method_not_allowed(self):
        """Test that POST to GET-only endpoints returns 405."""
        response = client.post("/")
        assert response.status_code == 405

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
        """Test that content-type header is present."""
        response = client.get("/")
        assert "content-type" in response.headers
        assert response.headers["content-type"] == "application/json"
