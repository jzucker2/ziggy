import os
import sys
from unittest.mock import Mock, patch

import pytest

# Add the app directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from app.main import initialize_mqtt_client
except ImportError:
    # Fallback for when running tests directly
    pass


class TestMQTTInitializationBug:
    """Test to verify that MQTT initialization doesn't call subscribe immediately."""

    @patch.dict(
        os.environ,
        {
            "MQTT_ENABLED": "true",
            "MQTT_BROKER_HOST": "test-broker",
            "MQTT_BROKER_PORT": "1883",
            "MQTT_CLIENT_ID": "test-client",
            "ZIGBEE2MQTT_HEALTH_TOPIC": "test/health",
        },
    )
    @patch("app.main.ZiggyMQTTClient")
    @pytest.mark.asyncio
    async def test_initialization_does_not_call_subscribe(
        self, mock_client_class
    ):
        """Test that initialize_mqtt_client doesn't call subscribe during initialization."""

        # Mock the ZiggyMQTTClient
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Set up mock attributes that the initialization function expects
        mock_client.zigbee2mqtt_health_topic = "test/health"
        mock_client.subscribed_topics = set()
        mock_client.mqtt = Mock()
        mock_client.metrics = Mock()

        # Mock the mqtt.subscribe method
        mock_client.mqtt.subscribe = Mock()

        # Call the initialization function
        result = await initialize_mqtt_client()

        # Verify that subscribe was NOT called during initialization
        mock_client.mqtt.subscribe.assert_not_called()

        # Verify the client was returned
        assert result == mock_client

        # Verify the topic was added to subscribed_topics
        assert "test/health" in mock_client.subscribed_topics

    @patch.dict(
        os.environ,
        {
            "MQTT_ENABLED": "true",
            "MQTT_BROKER_HOST": "test-broker",
            "MQTT_BROKER_PORT": "1883",
            "MQTT_CLIENT_ID": "test-client",
            "ZIGBEE2MQTT_HEALTH_TOPIC": "test/health",
        },
    )
    @patch("app.main.ZiggyMQTTClient")
    @pytest.mark.asyncio
    async def test_initialization_sets_up_client_correctly(
        self, mock_client_class
    ):
        """Test that initialization sets up the client correctly without premature subscription."""

        # Mock the ZiggyMQTTClient
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Set up mock attributes
        mock_client.broker_host = "test-broker"
        mock_client.broker_port = 1883
        mock_client.client_id = "test-client"
        mock_client.username = None
        mock_client.password = None
        mock_client.zigbee2mqtt_health_topic = "test/health"
        mock_client.subscribed_topics = set()
        mock_client.metrics = Mock()
        mock_client.mqtt = Mock()

        # Call the initialization function
        await initialize_mqtt_client()

        # Verify the client was marked as connected
        assert mock_client.connected is True

        # Verify metrics were updated
        mock_client.metrics.set_connection_status.assert_called_with(True)
        mock_client.metrics.set_client_info.assert_called()
        mock_client.metrics.set_subscriptions_active.assert_called_with(1)

        # Verify the topic was added to subscribed_topics
        assert "test/health" in mock_client.subscribed_topics

        # Verify subscribe was NOT called
        mock_client.mqtt.subscribe.assert_not_called()

    @patch.dict(os.environ, {"MQTT_ENABLED": "false"})
    @pytest.mark.asyncio
    async def test_initialization_returns_none_when_disabled(self):
        """Test that initialization returns None when MQTT is disabled."""

        result = await initialize_mqtt_client()

        assert result is None

    @patch.dict(
        os.environ,
        {
            "MQTT_ENABLED": "true"
            # MQTT_BROKER_HOST not set
        },
    )
    @pytest.mark.asyncio
    async def test_initialization_returns_none_when_no_broker_host(self):
        """Test that initialization returns None when MQTT_BROKER_HOST is not set."""

        # Clear MQTT_BROKER_HOST from environment
        if "MQTT_BROKER_HOST" in os.environ:
            del os.environ["MQTT_BROKER_HOST"]

        result = await initialize_mqtt_client()

        assert result is None
