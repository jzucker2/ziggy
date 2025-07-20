import asyncio
import json
import logging
import os
from typing import Any, Dict

from fastapi_mqtt import FastMQTT
from fastapi_mqtt.config import MQTTConfig

from app.mqtt_metrics import MQTTMetrics, set_mqtt_metrics
from app.zigbee2mqtt_metrics import Zigbee2MQTTMetrics, set_zigbee2mqtt_metrics

logger = logging.getLogger(__name__)


class ZiggyMQTTClient:
    """MQTT client for Ziggy API with metrics support."""

    def __init__(self):
        """Initialize the MQTT client with configuration from environment variables."""
        # MQTT Configuration
        self.broker_host = os.getenv("MQTT_BROKER_HOST", "localhost")
        self.broker_port = int(os.getenv("MQTT_BROKER_PORT", "1883"))
        self.username = os.getenv("MQTT_USERNAME")
        self.password = os.getenv("MQTT_PASSWORD")
        self.client_id = os.getenv("MQTT_CLIENT_ID", "ziggy-api")
        self.topic = os.getenv("MQTT_TOPIC", "zigbee2mqtt/#")
        self.zigbee2mqtt_health_topic = os.getenv(
            "ZIGBEE2MQTT_HEALTH_TOPIC", "zigbee2mqtt/bridge/health"
        )

        # Initialize metrics
        self.metrics = MQTTMetrics(
            self.broker_host, self.broker_port, self.client_id
        )
        set_mqtt_metrics(self.metrics)

        # Initialize Zigbee2MQTT metrics
        self.zigbee2mqtt_metrics = Zigbee2MQTTMetrics()
        set_zigbee2mqtt_metrics(self.zigbee2mqtt_metrics)

        # MQTT Client Configuration
        mqtt_config = MQTTConfig(
            host=self.broker_host,
            port=self.broker_port,
            keepalive=60,
            username=self.username,
            password=self.password,
            client_id=self.client_id,
        )

        self.mqtt = FastMQTT(config=mqtt_config)
        self.connected = False
        self.subscribed_topics = set()

        # Set up event handlers using decorators
        self._setup_event_handlers()

    def _setup_event_handlers(self):
        """Set up MQTT event handlers using decorators."""

        @self.mqtt.on_connect()
        def on_connect(client, flags, rc, properties=None):
            """Handle MQTT connection events."""
            if rc == 0:
                logger.info("Successfully connected to MQTT broker")
                self.connected = True
                self.metrics.set_connection_status(True)
            else:
                logger.error(
                    f"Failed to connect to MQTT broker with return code: {rc}"
                )
                self.connected = False
                self.metrics.set_connection_status(False)
                self.metrics.increment_connection_failures(f"rc_{rc}")

        @self.mqtt.on_disconnect()
        def on_disconnect(client, packet, exc=None):
            """Handle MQTT disconnection events."""
            logger.info("Disconnected from MQTT broker")
            self.connected = False
            self.metrics.set_connection_status(False)

        @self.mqtt.on_message()
        def on_message(client, topic, payload, qos, properties):
            """Handle incoming MQTT messages."""
            try:
                start_time = asyncio.get_event_loop().time()

                logger.debug(f"Received message on topic: {topic}")
                self.metrics.increment_messages_received(topic)
                self.metrics.observe_message_size(topic, len(payload))

                # Handle Zigbee2MQTT health messages
                if topic == self.zigbee2mqtt_health_topic:
                    self._handle_zigbee2mqtt_health(payload)
                else:
                    # Handle general messages
                    self._handle_general_message(topic, payload)

                # Calculate processing duration
                processing_time = asyncio.get_event_loop().time() - start_time
                self.metrics.observe_processing_duration(
                    topic, processing_time
                )

            except Exception as e:
                logger.error(
                    f"Error processing message from topic {topic}: {e}"
                )
                self.metrics.increment_processing_errors(
                    topic, str(type(e).__name__)
                )

    async def connect(self) -> bool:
        """Connect to the MQTT broker."""
        try:
            logger.info(
                f"Connecting to MQTT broker at {self.broker_host}:{self.broker_port}"
            )
            self.metrics.increment_connection_attempts()

            await self.mqtt.connect()
            self.connected = True
            self.metrics.set_connection_status(True)

            # Set client info
            client_info = {
                "connected": "true",
                "client_id": self.client_id,
                "broker_host": self.broker_host,
                "broker_port": str(self.broker_port),
                "has_credentials": (
                    "true" if self.username and self.password else "false"
                ),
            }
            self.metrics.set_client_info(client_info)

            logger.info("Successfully connected to MQTT broker")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            self.metrics.increment_connection_failures(str(type(e).__name__))
            self.metrics.set_connection_status(False)
            return False

    async def disconnect(self):
        """Disconnect from the MQTT broker."""
        try:
            if self.connected:
                await self.mqtt.disconnect()
                self.connected = False
                self.metrics.set_connection_status(False)
                logger.info("Disconnected from MQTT broker")
        except Exception as e:
            logger.error(f"Error disconnecting from MQTT broker: {e}")

    async def subscribe(self, topic: str) -> bool:
        """Subscribe to a topic."""
        try:
            if not self.connected:
                logger.warning(
                    "Cannot subscribe: not connected to MQTT broker"
                )
                return False

            logger.info(f"Subscribing to topic: {topic}")
            self.metrics.increment_subscription_attempts(topic)

            await self.mqtt.subscribe(topic)
            self.subscribed_topics.add(topic)

            # Update subscriptions count
            self.metrics.set_subscriptions_active(len(self.subscribed_topics))

            logger.info(f"Successfully subscribed to topic: {topic}")
            return True

        except Exception as e:
            logger.error(f"Failed to subscribe to topic {topic}: {e}")
            self.metrics.increment_subscription_failures(topic)
            return False

    async def publish(self, topic: str, message: str) -> bool:
        """Publish a message to a topic."""
        try:
            if not self.connected:
                logger.warning("Cannot publish: not connected to MQTT broker")
                return False

            logger.debug(f"Publishing message to topic: {topic}")
            self.metrics.increment_messages_published(topic)
            self.metrics.observe_message_size(
                topic, len(message.encode("utf-8"))
            )

            await self.mqtt.publish(topic, message)
            logger.debug(f"Successfully published message to topic: {topic}")
            return True

        except Exception as e:
            logger.error(f"Failed to publish message to topic {topic}: {e}")
            return False

    def _handle_zigbee2mqtt_health(self, payload):
        """Handle Zigbee2MQTT health messages."""
        try:
            # Decode payload
            if isinstance(payload, bytes):
                payload_str = payload.decode("utf-8")
            else:
                payload_str = str(payload)

            # Parse JSON
            health_data = json.loads(payload_str)

            # Update Zigbee2MQTT metrics
            self.zigbee2mqtt_metrics.update_bridge_health(health_data)

            logger.debug("Updated Zigbee2MQTT health metrics")

        except json.JSONDecodeError as e:
            logger.error(
                f"Failed to parse Zigbee2MQTT health data as JSON: {e}"
            )
            self.metrics.increment_processing_errors(
                self.zigbee2mqtt_health_topic, "json_parse_error"
            )
        except Exception as e:
            logger.error(f"Error handling Zigbee2MQTT health message: {e}")
            self.metrics.increment_processing_errors(
                self.zigbee2mqtt_health_topic, "handler_error"
            )

    def _handle_general_message(self, topic: str, payload):
        """Handle general MQTT messages."""
        try:
            # Decode payload
            if isinstance(payload, bytes):
                payload_str = payload.decode("utf-8")
            else:
                payload_str = str(payload)

            # Try to parse as JSON
            try:
                data = json.loads(payload_str)
                logger.debug(f"Received JSON message on topic {topic}: {data}")
            except json.JSONDecodeError:
                logger.debug(
                    f"Received non-JSON message on topic {topic}: {payload_str}"
                )

        except Exception as e:
            logger.error(
                f"Error handling general message from topic {topic}: {e}"
            )
            self.metrics.increment_processing_errors(topic, "general_error")

    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information."""
        return {
            "connected": self.connected,
            "broker_host": self.broker_host,
            "broker_port": self.broker_port,
            "client_id": self.client_id,
            "subscribed_topics": list(self.subscribed_topics),
            "has_credentials": bool(self.username and self.password),
        }
