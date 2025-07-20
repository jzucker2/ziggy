import json
import logging
import os
import time
from typing import Any, Dict, Optional

from fastapi_mqtt import FastMQTT, MQTTConfig
from gmqtt import Client as MQTTClient

from app.mqtt_metrics import MQTTMetrics, set_mqtt_metrics

logger = logging.getLogger(__name__)


class ZiggyMQTTClient:
    """MQTT client for subscribing to Zigbee topics using fastapi-mqtt."""

    def __init__(self):
        """Initialize MQTT client with configuration from environment variables."""
        # Get configuration from environment variables
        self.broker_host = os.getenv("MQTT_BROKER_HOST", "localhost")
        self.broker_port = int(os.getenv("MQTT_BROKER_PORT", "1883"))
        self.username = os.getenv("MQTT_USERNAME")
        self.password = os.getenv("MQTT_PASSWORD")
        self.topic = os.getenv("MQTT_ZIGBEE_TOPIC", "zigbee2mqtt/#")
        self.client_id = os.getenv("MQTT_CLIENT_ID", "ziggy-api")
        self.keepalive = int(os.getenv("MQTT_KEEPALIVE", "60"))

        # Initialize metrics
        self.metrics = MQTTMetrics(
            self.broker_host, self.broker_port, self.client_id
        )
        set_mqtt_metrics(self.metrics)

        # Create MQTT config
        mqtt_config = MQTTConfig(
            host=self.broker_host,
            port=self.broker_port,
            keepalive=self.keepalive,
            username=self.username,
            password=self.password,
        )

        # Initialize FastMQTT
        self.fast_mqtt = FastMQTT(config=mqtt_config)
        self.connected = False
        self.message_handlers = {}

        # Set up callbacks
        self._setup_callbacks()

    def _setup_callbacks(self):
        """Set up MQTT callbacks."""

        @self.fast_mqtt.on_connect()
        def connect(client: MQTTClient, flags: int, rc: int, properties: Any):
            """Callback for when the client connects to the broker."""
            if rc == 0:
                self.connected = True
                self.metrics.set_connection_status(True)
                self.metrics.set_client_info(
                    {
                        "connected": "true",
                        "client_id": self.client_id,
                        "broker_host": self.broker_host,
                        "broker_port": str(self.broker_port),
                        "has_credentials": str(
                            bool(self.username and self.password)
                        ),
                    }
                )
                logger.info(
                    f"Connected to MQTT broker at {self.broker_host}:{self.broker_port}"
                )

                # Subscribe to the Zigbee topic
                client.subscribe(self.topic)
                self.metrics.increment_subscription_attempts(self.topic)
                self.metrics.set_subscriptions_active(1)
                logger.info(f"Subscribed to topic: {self.topic}")
            else:
                self.connected = False
                self.metrics.set_connection_status(False)
                self.metrics.increment_connection_failures(f"rc_{rc}")
                logger.error(
                    f"Failed to connect to MQTT broker. Return code: {rc}"
                )

        @self.fast_mqtt.on_disconnect()
        def disconnect(client: MQTTClient, packet, exc=None):
            """Callback for when the client disconnects from the broker."""
            self.connected = False
            self.metrics.set_connection_status(False)
            self.metrics.set_subscriptions_active(0)
            if exc:
                self.metrics.increment_connection_failures("disconnect_error")
                logger.warning(
                    f"Unexpected disconnection from MQTT broker: {exc}"
                )
            else:
                logger.info("Disconnected from MQTT broker")

        @self.fast_mqtt.on_subscribe()
        def subscribe(client: MQTTClient, mid: int, qos: int, properties: Any):
            """Callback for when a subscription is successful."""
            logger.info(f"Successfully subscribed with QoS: {qos}")

        @self.fast_mqtt.subscribe(self.topic)
        async def handle_zigbee_message(
            client: MQTTClient,
            topic: str,
            payload: bytes,
            qos: int,
            properties: Any,
        ):
            """Handle incoming Zigbee messages from MQTT."""
            start_time = time.time()
            try:
                payload_str = payload.decode("utf-8")
                payload_size = len(payload)

                # Update metrics
                self.metrics.increment_messages_received(topic)
                self.metrics.observe_message_size(topic, payload_size)

                logger.debug(
                    f"Received message on topic {topic}: {payload_str}"
                )

                # Try to parse as JSON
                try:
                    data = json.loads(payload_str)
                    logger.info(f"Received JSON message on {topic}: {data}")
                except json.JSONDecodeError:
                    logger.info(
                        f"Received non-JSON message on {topic}: {payload_str}"
                    )
                    data = payload_str

                # Call registered handlers
                if topic in self.message_handlers:
                    try:
                        await self.message_handlers[topic](topic, data)
                    except Exception as e:
                        self.metrics.increment_processing_errors(
                            topic, "handler_error"
                        )
                        logger.error(
                            f"Error in message handler for topic {topic}: {e}"
                        )
                else:
                    # Call wildcard handler if no specific handler
                    wildcard_handler = self.message_handlers.get("*")
                    if wildcard_handler:
                        try:
                            await wildcard_handler(topic, data)
                        except Exception as e:
                            self.metrics.increment_processing_errors(
                                topic, "wildcard_handler_error"
                            )
                            logger.error(
                                f"Error in wildcard message handler: {e}"
                            )

                # Record processing duration
                processing_time = time.time() - start_time
                self.metrics.observe_processing_duration(
                    topic, processing_time
                )

            except Exception as e:
                self.metrics.increment_processing_errors(
                    topic, "general_error"
                )
                logger.error(f"Error processing MQTT message: {e}")

    async def connect(self) -> bool:
        """Connect to the MQTT broker."""
        try:
            logger.info(
                f"Connecting to MQTT broker at {self.broker_host}:{self.broker_port}"
            )
            self.metrics.increment_connection_attempts()
            await self.fast_mqtt.mqtt_startup()
            return True
        except Exception as e:
            self.metrics.increment_connection_failures("connection_exception")
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False

    async def disconnect(self):
        """Disconnect from the MQTT broker."""
        try:
            await self.fast_mqtt.mqtt_shutdown()
            self.metrics.reset_connection_status()
            logger.info("Disconnected from MQTT broker")
        except Exception as e:
            logger.error(f"Error disconnecting from MQTT broker: {e}")

    def add_message_handler(self, topic: str, handler):
        """
        Add a message handler for a specific topic.

        Args:
            topic: The topic to handle (use "*" for wildcard)
            handler: Async function to call when message is received
                   Signature: handler(topic: str, data: Any)
        """
        self.message_handlers[topic] = handler
        logger.info(f"Added message handler for topic: {topic}")

    def remove_message_handler(self, topic: str):
        """Remove a message handler for a specific topic."""
        if topic in self.message_handlers:
            del self.message_handlers[topic]
            logger.info(f"Removed message handler for topic: {topic}")

    def publish(self, topic: str, payload: str, qos: int = 0) -> bool:
        """
        Publish a message to a topic.

        Args:
            topic: The topic to publish to
            payload: The message payload
            qos: Quality of Service level (0, 1, or 2)

        Returns:
            True if successful, False otherwise
        """
        try:
            self.fast_mqtt.publish(topic, payload, qos)
            self.metrics.increment_messages_published(topic)
            self.metrics.observe_message_size(
                topic, len(payload.encode("utf-8"))
            )
            logger.debug(f"Published message to {topic}: {payload}")
            return True
        except Exception as e:
            self.metrics.increment_processing_errors(topic, "publish_error")
            logger.error(f"Error publishing message to {topic}: {e}")
            return False

    def is_connected(self) -> bool:
        """Check if the client is connected to the broker."""
        return self.connected

    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information."""
        return {
            "connected": self.connected,
            "broker_host": self.broker_host,
            "broker_port": self.broker_port,
            "topic": self.topic,
            "client_id": self.client_id,
            "has_credentials": bool(self.username and self.password),
        }

    def get_fast_mqtt(self) -> FastMQTT:
        """Get the underlying FastMQTT instance."""
        return self.fast_mqtt


# Global MQTT client instance
mqtt_client: Optional[ZiggyMQTTClient] = None


def get_mqtt_client() -> Optional[ZiggyMQTTClient]:
    """Get the global MQTT client instance."""
    return mqtt_client


async def initialize_mqtt_client() -> Optional[ZiggyMQTTClient]:
    """Initialize and return the global MQTT client."""
    global mqtt_client

    # Check if MQTT is enabled
    if not os.getenv("MQTT_ENABLED", "false").lower() == "true":
        logger.info("MQTT is disabled. Set MQTT_ENABLED=true to enable.")
        return None

    # Check required environment variables
    if not os.getenv("MQTT_BROKER_HOST"):
        logger.warning(
            "MQTT_BROKER_HOST not set. MQTT client will not be initialized."
        )
        return None

    try:
        mqtt_client = ZiggyMQTTClient()
        if await mqtt_client.connect():
            logger.info("MQTT client initialized successfully")
            return mqtt_client
        else:
            logger.error("Failed to initialize MQTT client")
            return None
    except Exception as e:
        logger.error(f"Error initializing MQTT client: {e}")
        return None


async def cleanup_mqtt_client():
    """Clean up the global MQTT client."""
    global mqtt_client
    if mqtt_client:
        await mqtt_client.disconnect()
        mqtt_client = None
        logger.info("MQTT client cleaned up")
