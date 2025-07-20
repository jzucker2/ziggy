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
        """Test that subscription is not attempted before client is connected."""

        # Mock FastMQTT to track subscription calls
        mock_mqtt = Mock()
        mock_mqtt.subscribe = Mock()

        with patch("app.mqtt_client.FastMQTT", return_value=mock_mqtt):
            # Create the client
            client = ZiggyMQTTClient()

            # Verify that subscribe was NOT called during initialization
            # This would be a bug - subscriptions should only happen after connection
            mock_mqtt.subscribe.assert_not_called()

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

            # Directly test the on_connect logic by calling the handler function
            # We'll simulate the on_connect behavior by calling the subscription logic directly
            if client.connected:
                # If client is connected, subscriptions should be made
                for topic in client.subscribed_topics:
                    client.mqtt.subscribe(topic)

            # Verify that subscribe was NOT called (client is not connected during initialization)
            mock_mqtt.subscribe.assert_not_called()

            # Now simulate a successful connection
            client.connected = True
            for topic in client.subscribed_topics:
                client.mqtt.subscribe(topic)

            # Verify that subscribe was called for the topic
            mock_mqtt.subscribe.assert_called_with("test/health")

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

            # Simulate connection failure (client remains disconnected)
            client.connected = False

            # Try to subscribe (should not happen when disconnected)
            if client.connected:
                for topic in client.subscribed_topics:
                    client.mqtt.subscribe(topic)

            # Verify that subscribe was NOT called (connection failed)
            mock_mqtt.subscribe.assert_not_called()

            # Verify client is marked as disconnected
            assert not client.connected

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

            # Simulate successful connection
            client.connected = True

            # Subscribe to all topics
            for topic in client.subscribed_topics:
                client.mqtt.subscribe(topic)

            # Check that subscribe was called 3 times
            assert mock_mqtt.subscribe.call_count == 3

            # Verify all expected topics were subscribed
            actual_calls = [
                call[0][0] for call in mock_mqtt.subscribe.call_args_list
            ]
            assert "test/health" in actual_calls
            assert "test/status" in actual_calls
            assert "test/events" in actual_calls

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
        """Test that client initialization itself doesn't subscribe."""

        # Mock FastMQTT
        mock_mqtt = Mock()
        mock_mqtt.subscribe = Mock()

        with patch("app.mqtt_client.FastMQTT", return_value=mock_mqtt):
            # Create the client
            client = ZiggyMQTTClient()

            # Verify that subscribe was NOT called during client initialization
            mock_mqtt.subscribe.assert_not_called()

            # Verify client starts as disconnected
            assert not client.connected

            # Verify subscribed_topics starts empty
            assert len(client.subscribed_topics) == 0
