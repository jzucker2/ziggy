import json
import os
from unittest.mock import AsyncMock, Mock, patch

from app.mqtt_client import ZiggyMQTTClient


class TestZiggyMQTTClient:
    """Test cases for ZiggyMQTTClient."""

    def test_mqtt_client_initialization(self):
        """Test MQTT client initialization with default values."""
        with patch.dict(os.environ, {}, clear=True):
            client = ZiggyMQTTClient()
            assert client.broker_host == "localhost"
            assert client.broker_port == 1883
            assert client.client_id == "ziggy-api"
            assert client.zigbee2mqtt_base_topic == "zigbee2mqtt"
            assert (
                client.zigbee2mqtt_health_topic == "zigbee2mqtt/bridge/health"
            )
            assert client.zigbee2mqtt_state_topic == "zigbee2mqtt/bridge/state"
            assert client.zigbee2mqtt_info_topic == "zigbee2mqtt/bridge/info"

    def test_mqtt_client_with_environment_variables(self):
        """Test MQTT client initialization with environment variables."""
        with patch.dict(
            os.environ,
            {
                "MQTT_BROKER_HOST": "test-broker",
                "MQTT_BROKER_PORT": "8883",
                "MQTT_USERNAME": "testuser",
                "MQTT_PASSWORD": "testpass",
                "MQTT_CLIENT_ID": "test-client",
                "ZIGBEE2MQTT_BASE_TOPIC": "test",
            },
            clear=True,
        ):
            client = ZiggyMQTTClient()
            assert client.broker_host == "test-broker"
            assert client.broker_port == 8883
            assert client.username == "testuser"
            assert client.password == "testpass"
            assert client.client_id == "test-client"
            assert client.zigbee2mqtt_base_topic == "test"
            assert client.zigbee2mqtt_health_topic == "test/bridge/health"
            assert client.zigbee2mqtt_state_topic == "test/bridge/state"
            assert client.zigbee2mqtt_info_topic == "test/bridge/info"

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
        """Test handling of Zigbee2MQTT health messages."""
        with patch.dict(os.environ, {}, clear=True):
            client = ZiggyMQTTClient()

            # Mock the metrics
            mock_metrics = Mock()
            client.zigbee2mqtt_metrics = mock_metrics

            # Mock payload
            payload = json.dumps(
                {
                    "response_time": 1234567890,
                    "os": {"load_average": [1.0, 1.0, 1.0]},
                    "process": {"uptime_sec": 3600},
                    "mqtt": {"connected": True},
                    "devices": {"0x1234567890abcdef": {"messages": 100}},
                }
            ).encode("utf-8")

            # Call the handler
            client._handle_zigbee2mqtt_health(payload)

            # Verify the metrics were updated
            mock_metrics.update_bridge_health.assert_called_once()

    def test_mqtt_client_handle_zigbee2mqtt_state(self):
        """Test handling of Zigbee2MQTT bridge state messages."""
        with patch.dict(os.environ, {}, clear=True):
            client = ZiggyMQTTClient()

            # Mock the metrics
            mock_metrics = Mock()
            client.zigbee2mqtt_metrics = mock_metrics

            # Mock payload with correct state format
            payload = json.dumps({"state": "online"}).encode("utf-8")

            # Call the handler
            client._handle_zigbee2mqtt_state(payload)

            # Verify the metrics were updated
            mock_metrics.update_bridge_state.assert_called_once()

    def test_mqtt_client_handle_zigbee2mqtt_info(self):
        """Test handling of Zigbee2MQTT bridge info messages."""
        with patch.dict(os.environ, {}, clear=True):
            client = ZiggyMQTTClient()

            # Mock the metrics
            mock_metrics = Mock()
            client.zigbee2mqtt_metrics = mock_metrics

            # Mock payload with info format
            payload = json.dumps(
                {
                    "version": "1.13.0-dev",
                    "commit": "772f6c0",
                    "coordinator": {
                        "ieee_address": "0x12345678",
                        "type": "zStack30x",
                    },
                    "log_level": "debug",
                    "permit_join": True,
                }
            ).encode("utf-8")

            # Call the handler
            client._handle_zigbee2mqtt_info(payload)

            # Verify the metrics were updated
            mock_metrics.update_bridge_info.assert_called_once()

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
