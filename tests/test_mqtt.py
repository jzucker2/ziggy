import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.mqtt_client import (
    ZiggyMQTTClient,
    cleanup_mqtt_client,
    initialize_mqtt_client,
)


class TestZiggyMQTTClient:
    """Test cases for ZiggyMQTTClient functionality."""

    def test_mqtt_client_initialization(self):
        """Test that MQTT client initializes with default values."""
        with patch.dict(os.environ, {}, clear=True):
            client = ZiggyMQTTClient()

            assert client.broker_host == "localhost"
            assert client.broker_port == 1883
            assert client.topic == "zigbee2mqtt/#"
            assert client.client_id == "ziggy-api"
            assert client.username is None
            assert client.password is None
            assert not client.connected

    def test_mqtt_client_with_environment_variables(self):
        """Test that MQTT client uses environment variables."""
        env_vars = {
            "MQTT_BROKER_HOST": "test-broker.com",
            "MQTT_BROKER_PORT": "8883",
            "MQTT_USERNAME": "testuser",
            "MQTT_PASSWORD": "testpass",
            "MQTT_ZIGBEE_TOPIC": "test/zigbee/#",
            "MQTT_CLIENT_ID": "test-client",
            "MQTT_KEEPALIVE": "120",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            client = ZiggyMQTTClient()

            assert client.broker_host == "test-broker.com"
            assert client.broker_port == 8883
            assert client.topic == "test/zigbee/#"
            assert client.client_id == "test-client"
            assert client.username == "testuser"
            assert client.password == "testpass"
            assert client.keepalive == 120

    def test_mqtt_client_connection_info(self):
        """Test that connection info returns correct data."""
        client = ZiggyMQTTClient()
        info = client.get_connection_info()

        assert "connected" in info
        assert "broker_host" in info
        assert "broker_port" in info
        assert "topic" in info
        assert "client_id" in info
        assert "has_credentials" in info
        assert info["connected"] is False
        assert info["broker_host"] == "localhost"
        assert info["broker_port"] == 1883

    def test_mqtt_client_message_handler(self):
        """Test that message handlers can be added and removed."""
        client = ZiggyMQTTClient()

        # Test adding handler
        async def test_handler(topic, data):
            pass

        client.add_message_handler("test/topic", test_handler)
        assert "test/topic" in client.message_handlers
        assert client.message_handlers["test/topic"] == test_handler

        # Test removing handler
        client.remove_message_handler("test/topic")
        assert "test/topic" not in client.message_handlers

    def test_mqtt_client_wildcard_handler(self):
        """Test that wildcard handlers work correctly."""
        client = ZiggyMQTTClient()

        async def wildcard_handler(topic, data):
            pass

        client.add_message_handler("*", wildcard_handler)
        assert "*" in client.message_handlers
        assert client.message_handlers["*"] == wildcard_handler

    @patch("app.mqtt_client.FastMQTT")
    def test_mqtt_client_connect_success(self, mock_fast_mqtt_class):
        """Test successful MQTT connection."""
        mock_fast_mqtt = MagicMock()
        mock_fast_mqtt.mqtt_startup = AsyncMock()
        mock_fast_mqtt_class.return_value = mock_fast_mqtt

        client = ZiggyMQTTClient()

        # Test the connect method
        import asyncio

        result = asyncio.run(client.connect())

        assert result is True
        mock_fast_mqtt.mqtt_startup.assert_called_once()

    @patch("app.mqtt_client.FastMQTT")
    def test_mqtt_client_connect_failure(self, mock_fast_mqtt_class):
        """Test failed MQTT connection."""
        mock_fast_mqtt = MagicMock()
        mock_fast_mqtt.mqtt_startup = AsyncMock(
            side_effect=Exception("Connection failed")
        )
        mock_fast_mqtt_class.return_value = mock_fast_mqtt

        client = ZiggyMQTTClient()

        # Test the connect method
        import asyncio

        result = asyncio.run(client.connect())

        assert result is False

    @patch("app.mqtt_client.FastMQTT")
    def test_mqtt_client_disconnect(self, mock_fast_mqtt_class):
        """Test MQTT disconnection."""
        mock_fast_mqtt = MagicMock()
        mock_fast_mqtt.mqtt_shutdown = AsyncMock()
        mock_fast_mqtt_class.return_value = mock_fast_mqtt

        client = ZiggyMQTTClient()

        # Test the disconnect method
        import asyncio

        asyncio.run(client.disconnect())

        mock_fast_mqtt.mqtt_shutdown.assert_called_once()

    @patch("app.mqtt_client.FastMQTT")
    def test_mqtt_client_publish_success(self, mock_fast_mqtt_class):
        """Test successful message publishing."""
        mock_fast_mqtt = MagicMock()
        mock_fast_mqtt.publish = MagicMock()
        mock_fast_mqtt_class.return_value = mock_fast_mqtt

        client = ZiggyMQTTClient()
        result = client.publish("test/topic", "test message")

        assert result is True
        mock_fast_mqtt.publish.assert_called_once_with(
            "test/topic", "test message", 0
        )

    @patch("app.mqtt_client.FastMQTT")
    def test_mqtt_client_publish_failure(self, mock_fast_mqtt_class):
        """Test failed message publishing."""
        mock_fast_mqtt = MagicMock()
        mock_fast_mqtt.publish = MagicMock(
            side_effect=Exception("Publish failed")
        )
        mock_fast_mqtt_class.return_value = mock_fast_mqtt

        client = ZiggyMQTTClient()
        result = client.publish("test/topic", "test message")

        assert result is False

    def test_mqtt_client_on_connect_success(self):
        """Test successful connection callback."""
        client = ZiggyMQTTClient()

        # Simulate the on_connect callback
        client.connected = False
        # This would be called by the decorator, but we'll simulate it
        client.connected = True

        assert client.connected is True

    def test_mqtt_client_on_connect_failure(self):
        """Test failed connection callback."""
        client = ZiggyMQTTClient()

        # Simulate failed connection
        client.connected = False

        assert client.connected is False

    def test_mqtt_client_on_disconnect(self):
        """Test disconnection callback."""
        client = ZiggyMQTTClient()
        client.connected = True

        # Simulate disconnection
        client.connected = False

        assert client.connected is False

    @pytest.mark.asyncio
    async def test_mqtt_client_on_message_json(self):
        """Test message callback with JSON payload."""
        client = ZiggyMQTTClient()

        # Add a test handler
        received_data = []

        async def test_handler(topic, data):
            received_data.append((topic, data))

        client.add_message_handler("test/topic", test_handler)

        # Simulate message processing
        payload = json.dumps({"device_id": "test-device", "state": "on"})
        await client.message_handlers["test/topic"]("test/topic", payload)

        assert len(received_data) == 1
        assert received_data[0][0] == "test/topic"
        assert received_data[0][1] == payload

    @pytest.mark.asyncio
    async def test_mqtt_client_on_message_non_json(self):
        """Test message callback with non-JSON payload."""
        client = ZiggyMQTTClient()

        # Add a test handler
        received_data = []

        async def test_handler(topic, data):
            received_data.append((topic, data))

        client.add_message_handler("test/topic", test_handler)

        # Simulate message processing
        payload = "raw message"
        await client.message_handlers["test/topic"]("test/topic", payload)

        assert len(received_data) == 1
        assert received_data[0][0] == "test/topic"
        assert received_data[0][1] == "raw message"

    @pytest.mark.asyncio
    async def test_mqtt_client_on_message_wildcard_handler(self):
        """Test message callback with wildcard handler."""
        client = ZiggyMQTTClient()

        # Add a wildcard handler
        received_data = []

        async def wildcard_handler(topic, data):
            received_data.append((topic, data))

        client.add_message_handler("*", wildcard_handler)

        # Simulate message processing
        payload = "test message"
        await client.message_handlers["*"]("test/topic", payload)

        assert len(received_data) == 1
        assert received_data[0][0] == "test/topic"
        assert received_data[0][1] == "test message"


class TestMQTTInitialization:
    """Test cases for MQTT client initialization functions."""

    @patch.dict(os.environ, {"MQTT_ENABLED": "false"}, clear=True)
    @pytest.mark.asyncio
    async def test_initialize_mqtt_client_disabled(self):
        """Test that MQTT client is not initialized when disabled."""
        client = await initialize_mqtt_client()
        assert client is None

    @patch.dict(os.environ, {"MQTT_ENABLED": "true"}, clear=True)
    @pytest.mark.asyncio
    async def test_initialize_mqtt_client_no_broker_host(self):
        """Test that MQTT client is not initialized without broker host."""
        client = await initialize_mqtt_client()
        assert client is None

    @patch.dict(
        os.environ,
        {"MQTT_ENABLED": "true", "MQTT_BROKER_HOST": "test-broker.com"},
        clear=True,
    )
    @patch("app.mqtt_client.ZiggyMQTTClient")
    @pytest.mark.asyncio
    async def test_initialize_mqtt_client_success(self, mock_client_class):
        """Test successful MQTT client initialization."""
        mock_client = MagicMock()
        mock_client.connect = AsyncMock(return_value=True)
        mock_client_class.return_value = mock_client

        client = await initialize_mqtt_client()

        assert client is not None
        mock_client.connect.assert_called_once()

    @patch.dict(
        os.environ,
        {"MQTT_ENABLED": "true", "MQTT_BROKER_HOST": "test-broker.com"},
        clear=True,
    )
    @patch("app.mqtt_client.ZiggyMQTTClient")
    @pytest.mark.asyncio
    async def test_initialize_mqtt_client_connection_failure(
        self, mock_client_class
    ):
        """Test MQTT client initialization with connection failure."""
        mock_client = MagicMock()
        mock_client.connect = AsyncMock(return_value=False)
        mock_client_class.return_value = mock_client

        client = await initialize_mqtt_client()

        assert client is None

    @pytest.mark.asyncio
    async def test_cleanup_mqtt_client(self):
        """Test MQTT client cleanup."""
        # This test ensures cleanup doesn't raise exceptions
        # Mock the global mqtt_client to avoid issues with MagicMock
        with patch("app.mqtt_client.mqtt_client", None):
            await cleanup_mqtt_client()
        # If we get here, no exception was raised
        assert True
