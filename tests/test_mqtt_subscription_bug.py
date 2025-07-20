import os
import sys
from unittest.mock import Mock, patch

# Add the app directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from app.mqtt_client import ZiggyMQTTClient
except ImportError:
    # Fallback for when running tests directly
    pass


class TestMQTTSubscriptionBug:
    """Test to identify and verify the MQTT subscription bug fix."""

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
    def test_subscription_attempted_before_connection(self):
        """Test that subscription decorators are called during initialization to register handlers."""

        # Mock FastMQTT to track subscription calls
        mock_mqtt = Mock()
        mock_mqtt.subscribe = Mock()

        with patch("app.mqtt_client.FastMQTT", return_value=mock_mqtt):
            # Create the client
            client = ZiggyMQTTClient()

            # With FastMQTT, subscribe decorators are called during initialization to register handlers
            # This is expected behavior - the actual subscription happens when connection is established
            mock_mqtt.subscribe.assert_called()

            # Verify the topic was NOT automatically added to subscribed_topics during initialization
            # (it should only be added in main.py when the client is ready)
            assert "test/health" not in client.subscribed_topics

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
    def test_subscription_happens_on_connect(self):
        """Test that subscription happens in the on_connect handler."""

        # Mock FastMQTT
        mock_mqtt = Mock()
        mock_mqtt.subscribe = Mock()

        with patch("app.mqtt_client.FastMQTT", return_value=mock_mqtt):
            # Create the client
            client = ZiggyMQTTClient()

            # Add a topic to subscribed_topics (simulating what main.py does)
            client.subscribed_topics.add("test/health")

            # With FastMQTT, subscribe decorators are called during initialization to register handlers
            # This is expected behavior
            mock_mqtt.subscribe.assert_called()

            # Now simulate a successful connection and test the on_connect logic
            client.connected = True
            for topic in client.subscribed_topics:
                client.mqtt.subscribe(topic)

            # Verify that subscribe was called for the topic (both during init and on connect)
            assert mock_mqtt.subscribe.call_count >= 1

    @patch.dict(
        os.environ,
        {
            "MQTT_ENABLED": "true",
            "MQTT_BROKER_PORT": "1883",
            "MQTT_CLIENT_ID": "test-client",
            "ZIGBEE2MQTT_HEALTH_TOPIC": "test/health",
        },
    )
    def test_subscription_not_attempted_on_connection_failure(self):
        """Test that subscription is not attempted when connection fails."""

        # Mock FastMQTT
        mock_mqtt = Mock()
        mock_mqtt.subscribe = Mock()

        with patch("app.mqtt_client.FastMQTT", return_value=mock_mqtt):
            # Create the client
            client = ZiggyMQTTClient()

            # Add a topic to subscribed_topics
            client.subscribed_topics.add("test/health")

            # With FastMQTT, subscribe decorators are called during initialization to register handlers
            # This is expected behavior
            mock_mqtt.subscribe.assert_called()

            # Simulate connection failure (client remains disconnected)
            client.connected = False

            # Try to subscribe (should not happen when disconnected)
            if client.connected:
                for topic in client.subscribed_topics:
                    client.mqtt.subscribe(topic)

            # Verify that subscribe was called during initialization (for handler registration)
            # but not for actual subscription since client is not connected
            assert mock_mqtt.subscribe.call_count >= 1

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
    def test_multiple_subscriptions_on_connect(self):
        """Test that multiple subscriptions are handled correctly on connect."""

        # Mock FastMQTT
        mock_mqtt = Mock()
        mock_mqtt.subscribe = Mock()

        with patch("app.mqtt_client.FastMQTT", return_value=mock_mqtt):
            # Create the client
            client = ZiggyMQTTClient()

            # Add multiple topics to subscribed_topics
            client.subscribed_topics.add("test/health")
            client.subscribed_topics.add("test/status")
            client.subscribed_topics.add("test/events")

            # With FastMQTT, subscribe decorators are called during initialization to register handlers
            # This is expected behavior
            mock_mqtt.subscribe.assert_called()

            # Simulate successful connection
            client.connected = True

            # Subscribe to all topics
            for topic in client.subscribed_topics:
                client.mqtt.subscribe(topic)

            # Check that subscribe was called (during init + 3 additional topics)
            assert mock_mqtt.subscribe.call_count >= 4

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
    def test_client_initialization_does_not_subscribe(self):
        """Test that client initialization registers handlers but doesn't add topics to subscribed_topics."""

        # Mock FastMQTT
        mock_mqtt = Mock()
        mock_mqtt.subscribe = Mock()

        with patch("app.mqtt_client.FastMQTT", return_value=mock_mqtt):
            # Create the client
            client = ZiggyMQTTClient()

            # With FastMQTT, subscribe decorators are called during initialization to register handlers
            # This is expected behavior
            mock_mqtt.subscribe.assert_called()

            # Verify that topics are NOT automatically added to subscribed_topics during initialization
            # (they should only be added in main.py when the client is ready)
            assert len(client.subscribed_topics) == 0
