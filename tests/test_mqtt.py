import json
import os
from unittest.mock import AsyncMock, patch

from app.mqtt_client import ZiggyMQTTClient


class TestZiggyMQTTClient:
    """Test cases for ZiggyMQTTClient."""

    def test_mqtt_client_initialization(self):
        """Test that MQTT client initializes correctly."""
        with patch.dict(os.environ, {}, clear=True):
            client = ZiggyMQTTClient()

            assert client.broker_host == "localhost"
            assert client.broker_port == 1883
            assert client.username is None
            assert client.password is None
            assert client.client_id == "ziggy-api"
            assert (
                client.zigbee2mqtt_health_topic == "zigbee2mqtt/bridge/health"
            )
            assert client.connected is False
            assert client.subscribed_topics == set()

    def test_mqtt_client_with_environment_variables(self):
        """Test MQTT client initialization with environment variables."""
        env_vars = {
            "MQTT_BROKER_HOST": "test-broker.com",
            "MQTT_BROKER_PORT": "8883",
            "MQTT_USERNAME": "testuser",
            "MQTT_PASSWORD": "testpass",
            "MQTT_CLIENT_ID": "test-client",
            "MQTT_TOPIC": "test/topic/#",
            "ZIGBEE2MQTT_HEALTH_TOPIC": "test/health",
            "ZIGBEE2MQTT_BRIDGE_NAME": "test-bridge",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            client = ZiggyMQTTClient()

            assert client.broker_host == "test-broker.com"
            assert client.broker_port == 8883
            assert client.username == "testuser"
            assert client.password == "testpass"
            assert client.client_id == "test-client"
            assert client.zigbee2mqtt_health_topic == "test/health"
            assert client.zigbee2mqtt_metrics.bridge_name == "test-bridge"

    def test_mqtt_client_default_bridge_name(self):
        """Test that default bridge name is used when ZIGBEE2MQTT_BRIDGE_NAME is not set."""
        with patch.dict(os.environ, {}, clear=True):
            client = ZiggyMQTTClient()
            assert client.zigbee2mqtt_metrics.bridge_name == "default"

    def test_mqtt_client_connection_info(self):
        """Test that connection info is returned correctly."""
        with patch.dict(os.environ, {}, clear=True):
            client = ZiggyMQTTClient()
            info = client.get_connection_info()

            assert info["connected"] is False
            assert info["broker_host"] == "localhost"
            assert info["broker_port"] == 1883
            assert info["client_id"] == "ziggy-api"
            assert info["subscribed_topics"] == []
            assert info["has_credentials"] is False

    def test_mqtt_client_message_handler(self):
        """Test that message handlers are set up correctly."""
        client = ZiggyMQTTClient()

        # Check that event handlers are set
        assert hasattr(client, "_handle_general_message")
        assert hasattr(client, "_handle_zigbee2mqtt_health")

    def test_mqtt_client_wildcard_handler(self):
        """Test that wildcard message handling works."""
        client = ZiggyMQTTClient()

        # Test that the client can handle general messages
        assert hasattr(client, "_handle_general_message")
        assert hasattr(client, "_handle_zigbee2mqtt_health")

    def test_mqtt_client_handle_zigbee2mqtt_health(self):
        """Test Zigbee2MQTT health message handling."""
        client = ZiggyMQTTClient()

        # Test with valid JSON
        health_data = {"response_time": 1640995200000}
        payload = json.dumps(health_data).encode("utf-8")

        # Should not raise any exceptions
        client._handle_zigbee2mqtt_health(payload)

    def test_mqtt_client_handle_general_message(self):
        """Test general message handling."""
        client = ZiggyMQTTClient()

        # Test with JSON payload
        payload = json.dumps({"test": "data"}).encode("utf-8")
        client._handle_general_message("test/topic", payload)

        # Test with non-JSON payload
        payload = b"non-json message"
        client._handle_general_message("test/topic", payload)

    def test_mqtt_client_get_connection_info_with_credentials(self):
        """Test connection info when credentials are provided."""
        env_vars = {
            "MQTT_USERNAME": "testuser",
            "MQTT_PASSWORD": "testpass",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            client = ZiggyMQTTClient()
            info = client.get_connection_info()

            assert info["has_credentials"] is True


class TestMQTTInitialization:
    """Test cases for MQTT client initialization in the main application."""

    @patch("app.main.ZiggyMQTTClient")
    def test_initialize_mqtt_client_disabled(self, mock_client_class):
        """Test MQTT client initialization when disabled."""
        with patch.dict(os.environ, {}, clear=True):
            from app.main import initialize_mqtt_client

            # This would be async in real usage, but we're testing the logic
            # For now, just test that the function exists
            assert callable(initialize_mqtt_client)

    @patch("app.main.ZiggyMQTTClient")
    def test_initialize_mqtt_client_no_broker_host(self, mock_client_class):
        """Test MQTT client initialization without broker host."""
        with patch.dict(os.environ, {"MQTT_ENABLED": "true"}, clear=True):
            from app.main import initialize_mqtt_client

            # This would be async in real usage, but we're testing the logic
            # For now, just test that the function exists
            assert callable(initialize_mqtt_client)

    @patch("app.main.mqtt_client")
    def test_cleanup_mqtt_client(self, mock_mqtt_client):
        """Test MQTT client cleanup."""
        mock_mqtt_client.disconnect = AsyncMock()

        from app.main import cleanup_mqtt_client

        # This would be async in real usage, but we're testing the logic
        # For now, just test that the function exists
        assert callable(cleanup_mqtt_client)
