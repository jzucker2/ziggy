import os
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.main import initialize_mqtt_client, lifespan
from app.mqtt_client import ZiggyMQTTClient


class TestMQTTEnabledDefault:
    """Test cases for MQTT_ENABLED default behavior."""

    @patch("app.main.ZiggyMQTTClient")
    @pytest.mark.asyncio
    async def test_mqtt_enabled_defaults_to_true(self, mock_client_class):
        """Test that MQTT is enabled by default when MQTT_ENABLED is not set."""
        # Clear any existing MQTT_ENABLED from environment and set broker host
        with patch.dict(
            os.environ, {"MQTT_BROKER_HOST": "test-broker"}, clear=True
        ):
            # Mock the ZiggyMQTTClient
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Set up mock attributes
            mock_client.broker_host = "test-broker"
            mock_client.broker_port = 1883
            mock_client.client_id = "test-client"
            mock_client.username = None
            mock_client.password = None
            mock_client.zigbee2mqtt_base_topic = "test"
            mock_client.zigbee2mqtt_health_topic = "test/bridge/health"
            mock_client.zigbee2mqtt_state_topic = "test/bridge/state"
            mock_client.zigbee2mqtt_info_topic = "test/bridge/info"
            mock_client.subscribed_topics = set()
            mock_client.metrics = Mock()
            mock_client.mqtt = Mock()

            # Call the initialization function
            result = await initialize_mqtt_client()

            # Verify the client was created and returned
            assert result == mock_client
            mock_client_class.assert_called_once()

    @patch("app.main.ZiggyMQTTClient")
    @pytest.mark.asyncio
    async def test_mqtt_enabled_explicitly_true(self, mock_client_class):
        """Test that MQTT is enabled when MQTT_ENABLED is explicitly set to true."""
        with patch.dict(
            os.environ,
            {"MQTT_ENABLED": "true", "MQTT_BROKER_HOST": "test-broker"},
            clear=True,
        ):
            # Mock the ZiggyMQTTClient
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Set up mock attributes
            mock_client.broker_host = "test-broker"
            mock_client.broker_port = 1883
            mock_client.client_id = "test-client"
            mock_client.username = None
            mock_client.password = None
            mock_client.zigbee2mqtt_base_topic = "test"
            mock_client.zigbee2mqtt_health_topic = "test/bridge/health"
            mock_client.zigbee2mqtt_state_topic = "test/bridge/state"
            mock_client.zigbee2mqtt_info_topic = "test/bridge/info"
            mock_client.subscribed_topics = set()
            mock_client.metrics = Mock()
            mock_client.mqtt = Mock()

            # Call the initialization function
            result = await initialize_mqtt_client()

            # Verify the client was created and returned
            assert result == mock_client
            mock_client_class.assert_called_once()

    @pytest.mark.asyncio
    async def test_mqtt_enabled_explicitly_false(self):
        """Test that MQTT is disabled when MQTT_ENABLED is explicitly set to false."""
        with patch.dict(os.environ, {"MQTT_ENABLED": "false"}, clear=True):
            # Call the initialization function
            result = await initialize_mqtt_client()

            # Verify None is returned when MQTT is disabled
            assert result is None

    @pytest.mark.asyncio
    async def test_mqtt_enabled_case_insensitive(self):
        """Test that MQTT_ENABLED is case insensitive."""
        # Test with uppercase FALSE
        with patch.dict(os.environ, {"MQTT_ENABLED": "FALSE"}, clear=True):
            result = await initialize_mqtt_client()
            assert result is None

        # Test with mixed case True
        with patch.dict(
            os.environ,
            {"MQTT_ENABLED": "True", "MQTT_BROKER_HOST": "test-broker"},
            clear=True,
        ):
            with patch("app.main.ZiggyMQTTClient") as mock_client_class:
                mock_client = Mock()
                mock_client_class.return_value = mock_client
                mock_client.broker_host = "test-broker"
                mock_client.broker_port = 1883
                mock_client.client_id = "test-client"
                mock_client.username = None
                mock_client.password = None
                mock_client.zigbee2mqtt_base_topic = "test"
                mock_client.zigbee2mqtt_health_topic = "test/bridge/health"
                mock_client.zigbee2mqtt_state_topic = "test/bridge/state"
                mock_client.zigbee2mqtt_info_topic = "test/bridge/info"
                mock_client.subscribed_topics = set()
                mock_client.metrics = Mock()
                mock_client.mqtt = Mock()

                result = await initialize_mqtt_client()
                assert result == mock_client

    @pytest.mark.asyncio
    async def test_mqtt_enabled_no_broker_host(self):
        """Test that MQTT is disabled when MQTT_BROKER_HOST is not set."""
        with patch.dict(os.environ, {"MQTT_ENABLED": "true"}, clear=True):
            # Ensure MQTT_BROKER_HOST is not set
            if "MQTT_BROKER_HOST" in os.environ:
                del os.environ["MQTT_BROKER_HOST"]

            result = await initialize_mqtt_client()

            # Verify None is returned when broker host is not configured
            assert result is None


class TestFastMQTTIntegration:
    """Test cases for FastMQTT integration fixes."""

    @patch("app.main.ZiggyMQTTClient")
    @pytest.mark.asyncio
    async def test_fastmqtt_init_app_called(self, mock_client_class):
        """Test that FastMQTT init_app is called correctly."""
        with patch.dict(
            os.environ,
            {"MQTT_ENABLED": "true", "MQTT_BROKER_HOST": "test-broker"},
            clear=True,
        ):
            # Mock the ZiggyMQTTClient
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Set up mock attributes
            mock_client.broker_host = "test-broker"
            mock_client.broker_port = 1883
            mock_client.client_id = "test-client"
            mock_client.username = None
            mock_client.password = None
            mock_client.zigbee2mqtt_base_topic = "test"
            mock_client.zigbee2mqtt_health_topic = "test/bridge/health"
            mock_client.zigbee2mqtt_state_topic = "test/bridge/state"
            mock_client.zigbee2mqtt_info_topic = "test/bridge/info"
            mock_client.subscribed_topics = set()
            mock_client.metrics = Mock()
            mock_client.mqtt = Mock()
            mock_client.disconnect = AsyncMock()

            # Mock the FastAPI app
            mock_app = Mock()

            # Test the lifespan function
            async with lifespan(mock_app):
                # Verify that init_app was called
                mock_client.mqtt.init_app.assert_called_once_with(mock_app)

    @patch("app.main.ZiggyMQTTClient")
    @pytest.mark.asyncio
    async def test_fastmqtt_connection_called(self, mock_client_class):
        """Test that FastMQTT connection is called correctly."""
        with patch.dict(
            os.environ,
            {"MQTT_ENABLED": "true", "MQTT_BROKER_HOST": "test-broker"},
            clear=True,
        ):
            # Mock the ZiggyMQTTClient
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Set up mock attributes
            mock_client.broker_host = "test-broker"
            mock_client.broker_port = 1883
            mock_client.client_id = "test-client"
            mock_client.username = None
            mock_client.password = None
            mock_client.zigbee2mqtt_base_topic = "test"
            mock_client.zigbee2mqtt_health_topic = "test/bridge/health"
            mock_client.zigbee2mqtt_state_topic = "test/bridge/state"
            mock_client.zigbee2mqtt_info_topic = "test/bridge/info"
            mock_client.subscribed_topics = set()
            mock_client.metrics = Mock()
            mock_client.mqtt = Mock()
            mock_client.disconnect = AsyncMock()

            # Mock the FastAPI app
            mock_app = Mock()

            # Test the lifespan function
            async with lifespan(mock_app):
                # Verify that connection was called
                mock_client.mqtt.connection.assert_called_once()

    @patch("app.main.ZiggyMQTTClient")
    @pytest.mark.asyncio
    async def test_fastmqtt_connection_error_handled(self, mock_client_class):
        """Test that FastMQTT connection errors are handled gracefully."""
        with patch.dict(
            os.environ,
            {"MQTT_ENABLED": "true", "MQTT_BROKER_HOST": "test-broker"},
            clear=True,
        ):
            # Mock the ZiggyMQTTClient
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Set up mock attributes
            mock_client.broker_host = "test-broker"
            mock_client.broker_port = 1883
            mock_client.client_id = "test-client"
            mock_client.username = None
            mock_client.password = None
            mock_client.zigbee2mqtt_base_topic = "test"
            mock_client.zigbee2mqtt_health_topic = "test/bridge/health"
            mock_client.zigbee2mqtt_state_topic = "test/bridge/state"
            mock_client.zigbee2mqtt_info_topic = "test/bridge/info"
            mock_client.subscribed_topics = set()
            mock_client.metrics = Mock()
            mock_client.mqtt = Mock()
            mock_client.disconnect = AsyncMock()

            # Make connection raise an exception
            mock_client.mqtt.connection.side_effect = Exception(
                "Connection failed"
            )

            # Mock the FastAPI app
            mock_app = Mock()

            # Test the lifespan function - should not raise an exception
            async with lifespan(mock_app):
                # Verify that connection was attempted
                mock_client.mqtt.connection.assert_called_once()

    @patch("app.main.ZiggyMQTTClient")
    @pytest.mark.asyncio
    async def test_mqtt_client_disconnect_called_on_shutdown(
        self, mock_client_class
    ):
        """Test that MQTT client disconnect is called during shutdown."""
        with patch.dict(
            os.environ,
            {"MQTT_ENABLED": "true", "MQTT_BROKER_HOST": "test-broker"},
            clear=True,
        ):
            # Mock the ZiggyMQTTClient
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Set up mock attributes
            mock_client.broker_host = "test-broker"
            mock_client.broker_port = 1883
            mock_client.client_id = "test-client"
            mock_client.username = None
            mock_client.password = None
            mock_client.zigbee2mqtt_base_topic = "test"
            mock_client.zigbee2mqtt_health_topic = "test/bridge/health"
            mock_client.zigbee2mqtt_state_topic = "test/bridge/state"
            mock_client.zigbee2mqtt_info_topic = "test/bridge/info"
            mock_client.subscribed_topics = set()
            mock_client.metrics = Mock()
            mock_client.mqtt = Mock()

            # Mock the disconnect method
            mock_client.disconnect = AsyncMock()

            # Mock the FastAPI app
            mock_app = Mock()

            # Test the lifespan function
            async with lifespan(mock_app):
                pass  # This will trigger the shutdown part

            # Verify that disconnect was called
            mock_client.disconnect.assert_called_once()


class TestMQTTClientInitialization:
    """Test cases for MQTT client initialization with new defaults."""

    def test_mqtt_client_initialization_with_defaults(self):
        """Test MQTT client initialization with default MQTT_ENABLED behavior."""
        with patch.dict(os.environ, {}, clear=True):
            # Test that client can be initialized when MQTT_ENABLED defaults to true
            # and MQTT_BROKER_HOST is provided
            with patch.dict(
                os.environ, {"MQTT_BROKER_HOST": "test-broker"}, clear=False
            ):
                client = ZiggyMQTTClient()

                # Verify the client was created successfully
                assert client is not None
                assert client.broker_host == "test-broker"
                assert client.broker_port == 1883
                assert client.client_id == "ziggy-api"

    def test_mqtt_client_initialization_with_explicit_enabled(self):
        """Test MQTT client initialization with explicit MQTT_ENABLED=true."""
        with patch.dict(
            os.environ,
            {"MQTT_ENABLED": "true", "MQTT_BROKER_HOST": "test-broker"},
            clear=True,
        ):
            client = ZiggyMQTTClient()

            # Verify the client was created successfully
            assert client is not None
            assert client.broker_host == "test-broker"
            assert client.broker_port == 1883
            assert client.client_id == "ziggy-api"

    def test_mqtt_client_initialization_with_explicit_disabled(self):
        """Test MQTT client initialization with explicit MQTT_ENABLED=false."""
        with patch.dict(
            os.environ,
            {"MQTT_ENABLED": "false", "MQTT_BROKER_HOST": "test-broker"},
            clear=True,
        ):
            # This should still create a client object, but the main app won't use it
            # The actual disabling happens in the main app's initialize_mqtt_client function
            client = ZiggyMQTTClient()

            # Verify the client was created (the disabling logic is in main.py)
            assert client is not None
            assert client.broker_host == "test-broker"


class TestMQTTEnvironmentVariableConsistency:
    """Test cases for MQTT environment variable consistency."""

    def test_mqtt_enabled_vs_mqtt_disabled_consistency(self):
        """Test that the codebase consistently uses MQTT_ENABLED instead of MQTT_DISABLED."""
        # Check that the main application logic uses MQTT_ENABLED
        with patch.dict(
            os.environ,
            {"MQTT_ENABLED": "true", "MQTT_BROKER_HOST": "test-broker"},
            clear=True,
        ):
            # This should work with MQTT_ENABLED
            with patch("app.main.ZiggyMQTTClient") as mock_client_class:
                mock_client = Mock()
                mock_client_class.return_value = mock_client
                mock_client.broker_host = "test-broker"
                mock_client.broker_port = 1883
                mock_client.client_id = "test-client"
                mock_client.username = None
                mock_client.password = None
                mock_client.zigbee2mqtt_base_topic = "test"
                mock_client.zigbee2mqtt_health_topic = "test/bridge/health"
                mock_client.zigbee2mqtt_state_topic = "test/bridge/state"
                mock_client.zigbee2mqtt_info_topic = "test/bridge/info"
                mock_client.subscribed_topics = set()
                mock_client.metrics = Mock()
                mock_client.mqtt = Mock()

                # The function should work with MQTT_ENABLED
                import asyncio

                result = asyncio.run(initialize_mqtt_client())
                assert result == mock_client

    def test_environment_variable_precedence(self):
        """Test that MQTT_ENABLED takes precedence over any legacy MQTT_DISABLED."""
        # Test with both variables set - MQTT_ENABLED should take precedence
        with patch.dict(
            os.environ,
            {
                "MQTT_ENABLED": "true",
                "MQTT_DISABLED": "true",  # This should be ignored
                "MQTT_BROKER_HOST": "test-broker",
            },
            clear=True,
        ):
            with patch("app.main.ZiggyMQTTClient") as mock_client_class:
                mock_client = Mock()
                mock_client_class.return_value = mock_client
                mock_client.broker_host = "test-broker"
                mock_client.broker_port = 1883
                mock_client.client_id = "test-client"
                mock_client.username = None
                mock_client.password = None
                mock_client.zigbee2mqtt_base_topic = "test"
                mock_client.zigbee2mqtt_health_topic = "test/bridge/health"
                mock_client.zigbee2mqtt_state_topic = "test/bridge/state"
                mock_client.zigbee2mqtt_info_topic = "test/bridge/info"
                mock_client.subscribed_topics = set()
                mock_client.metrics = Mock()
                mock_client.mqtt = Mock()

                # MQTT_ENABLED=true should take precedence over MQTT_DISABLED=true
                import asyncio

                result = asyncio.run(initialize_mqtt_client())
                assert result == mock_client
