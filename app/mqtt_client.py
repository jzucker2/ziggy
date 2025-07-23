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

        # Zigbee2MQTT Configuration
        self.zigbee2mqtt_base_topic = os.getenv(
            "ZIGBEE2MQTT_BASE_TOPIC", "zigbee2mqtt"
        )
        self.zigbee2mqtt_health_topic = (
            f"{self.zigbee2mqtt_base_topic}/bridge/health"
        )
        self.zigbee2mqtt_state_topic = (
            f"{self.zigbee2mqtt_base_topic}/bridge/state"
        )

        # Initialize metrics
        self.metrics = MQTTMetrics(
            self.broker_host, self.broker_port, self.client_id
        )
        set_mqtt_metrics(self.metrics)

        # Initialize Zigbee2MQTT metrics
        bridge_name = os.getenv("ZIGBEE2MQTT_BRIDGE_NAME", "default")
        self.zigbee2mqtt_metrics = Zigbee2MQTTMetrics(
            bridge_name, self.zigbee2mqtt_base_topic
        )
        set_zigbee2mqtt_metrics(self.zigbee2mqtt_metrics)

        # Set base topic info
        self.zigbee2mqtt_metrics.set_base_topic_info(
            {
                "base_topic": self.zigbee2mqtt_base_topic,
                "health_topic": self.zigbee2mqtt_health_topic,
                "state_topic": self.zigbee2mqtt_state_topic,
            }
        )

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
            logger.info(
                f"🔌 MQTT on_connect event triggered - flags: {flags}, rc: {rc}, properties: {properties}"
            )
            logger.debug(
                f"MQTT on_connect event triggered - flags: {flags}, rc: {rc}, properties: {properties}"
            )

            if rc == 0:
                logger.info("✅ Successfully connected to MQTT broker")
                logger.debug(
                    f"Connection details - broker: {self.broker_host}:{self.broker_port}, client_id: {self.client_id}"
                )
                self.connected = True
                self.metrics.set_connection_status(True)

                # Re-subscribe to topics when connection is established
                logger.info(
                    f"📡 Connection established - re-subscribing to topics: {list(self.subscribed_topics)}"
                )
                logger.debug(
                    f"Connection established - re-subscribing to topics: {list(self.subscribed_topics)}"
                )
                for topic in self.subscribed_topics:
                    logger.info(f"📡 Re-subscribing to topic: {topic}")
                    logger.debug(f"Re-subscribing to topic: {topic}")
                    try:
                        self.mqtt.subscribe(topic)
                        logger.info(
                            f"✅ Successfully subscribed to topic: {topic}"
                        )
                        logger.debug(
                            f"Subscription call completed for topic: {topic}"
                        )
                    except Exception as e:
                        logger.error(
                            f"❌ Failed to subscribe to topic {topic}: {e}"
                        )
                        logger.debug(
                            f"Subscription error details - topic: {topic}, exception_type: {type(e).__name__}, exception_args: {e.args}"
                        )

            else:
                logger.error(
                    f"❌ Failed to connect to MQTT broker with return code: {rc}"
                )
                logger.debug(
                    f"Connection failure details - broker: {self.broker_host}:{self.broker_port}, client_id: {self.client_id}"
                )
                self.connected = False
                self.metrics.set_connection_status(False)
                self.metrics.increment_connection_failures(f"rc_{rc}")

        @self.mqtt.on_disconnect()
        def on_disconnect(client, packet, exc=None):
            """Handle MQTT disconnection events."""
            logger.info(
                f"🔌 MQTT on_disconnect event triggered - packet: {packet}, exc: {exc}"
            )
            logger.debug(
                f"MQTT on_disconnect event triggered - packet: {packet}, exc: {exc}"
            )
            logger.info("❌ Disconnected from MQTT broker")
            self.connected = False
            self.metrics.set_connection_status(False)

        @self.mqtt.subscribe(self.zigbee2mqtt_health_topic)
        async def on_health_message(client, topic, payload, qos, properties):
            """Handle incoming Zigbee2MQTT health messages."""
            logger.info(
                f"🎯 MQTT HEALTH MESSAGE HANDLER CALLED - topic: {topic}"
            )
            logger.debug(
                f"MQTT health message handler called - topic: {topic}, payload_size: {len(payload) if payload else 0}"
            )

            try:
                start_time = asyncio.get_event_loop().time()

                logger.info(
                    f"🎯 MQTT HEALTH MESSAGE RECEIVED - topic: {topic}, qos: {qos}, payload_size: {len(payload)} bytes"
                )
                logger.debug(
                    f"MQTT health message received - topic: {topic}, qos: {qos}, payload_size: {len(payload)} bytes"
                )
                logger.debug(f"Message properties: {properties}")

                # Log payload preview (first 200 chars for safety)
                payload_preview = str(payload)[:200]
                if len(str(payload)) > 200:
                    payload_preview += "..."
                logger.debug(f"Message payload preview: {payload_preview}")

                self.metrics.increment_messages_received(topic)
                self.metrics.observe_message_size(topic, len(payload))

                logger.info(
                    f"🏥 Processing Zigbee2MQTT health message on topic: {topic}"
                )
                logger.debug(
                    f"Processing Zigbee2MQTT health message on topic: {topic}"
                )
                self._handle_zigbee2mqtt_health(payload)

                # Calculate processing duration
                processing_time = asyncio.get_event_loop().time() - start_time
                logger.debug(
                    f"Health message processing completed in {processing_time:.4f}s"
                )
                self.metrics.observe_processing_duration(
                    topic, processing_time
                )

            except Exception as e:
                logger.error(
                    f"Error processing health message from topic {topic}: {e}"
                )
                logger.debug(
                    f"Error details - payload_size: {len(payload)}, exception_type: {type(e).__name__}"
                )
                self.metrics.increment_processing_errors(
                    topic, str(type(e).__name__)
                )

        @self.mqtt.subscribe(self.zigbee2mqtt_state_topic)
        async def on_state_message(client, topic, payload, qos, properties):
            """Handle incoming Zigbee2MQTT bridge state messages."""
            logger.info(
                f"🎯 MQTT STATE MESSAGE HANDLER CALLED - topic: {topic}"
            )
            logger.debug(
                f"MQTT state message handler called - topic: {topic}, payload_size: {len(payload) if payload else 0}"
            )

            try:
                start_time = asyncio.get_event_loop().time()

                logger.info(
                    f"🎯 MQTT STATE MESSAGE RECEIVED - topic: {topic}, qos: {qos}, payload_size: {len(payload)} bytes"
                )
                logger.debug(
                    f"MQTT state message received - topic: {topic}, qos: {qos}, payload_size: {len(payload)} bytes"
                )
                logger.debug(f"Message properties: {properties}")

                # Log payload preview (first 200 chars for safety)
                payload_preview = str(payload)[:200]
                if len(str(payload)) > 200:
                    payload_preview += "..."
                logger.debug(f"Message payload preview: {payload_preview}")

                self.metrics.increment_messages_received(topic)
                self.metrics.observe_message_size(topic, len(payload))

                logger.info(
                    f"🏗️ Processing Zigbee2MQTT bridge state message on topic: {topic}"
                )
                logger.debug(
                    f"Processing Zigbee2MQTT bridge state message on topic: {topic}"
                )
                self._handle_zigbee2mqtt_state(payload)

                # Calculate processing duration
                processing_time = asyncio.get_event_loop().time() - start_time
                logger.debug(
                    f"State message processing completed in {processing_time:.4f}s"
                )
                self.metrics.observe_processing_duration(
                    topic, processing_time
                )

            except Exception as e:
                logger.error(
                    f"Error processing state message from topic {topic}: {e}"
                )
                logger.debug(
                    f"Error details - payload_size: {len(payload)}, exception_type: {type(e).__name__}"
                )
                self.metrics.increment_processing_errors(
                    topic, str(type(e).__name__)
                )

        @self.mqtt.subscribe("#")
        async def on_message(client, topic, payload, qos, properties):
            """Handle incoming MQTT messages."""
            logger.info(f"🎯 MQTT MESSAGE HANDLER CALLED - topic: {topic}")
            logger.debug(
                f"MQTT message handler called - topic: {topic}, payload_size: {len(payload) if payload else 0}"
            )

            try:
                start_time = asyncio.get_event_loop().time()

                logger.info(
                    f"🎯 MQTT MESSAGE RECEIVED - topic: {topic}, qos: {qos}, payload_size: {len(payload)} bytes"
                )
                logger.debug(
                    f"MQTT message received - topic: {topic}, qos: {qos}, payload_size: {len(payload)} bytes"
                )
                logger.debug(f"Message properties: {properties}")

                # Log payload preview (first 200 chars for safety)
                payload_preview = str(payload)[:200]
                if len(str(payload)) > 200:
                    payload_preview += "..."
                logger.debug(f"Message payload preview: {payload_preview}")

                self.metrics.increment_messages_received(topic)
                self.metrics.observe_message_size(topic, len(payload))

                # Handle Zigbee2MQTT health messages
                if topic == self.zigbee2mqtt_health_topic:
                    logger.info(
                        f"🏥 Processing Zigbee2MQTT health message on topic: {topic}"
                    )
                    logger.debug(
                        f"Processing Zigbee2MQTT health message on topic: {topic}"
                    )
                    self._handle_zigbee2mqtt_health(payload)
                elif topic == self.zigbee2mqtt_state_topic:
                    logger.info(
                        f"🏗️ Processing Zigbee2MQTT bridge state message on topic: {topic}"
                    )
                    logger.debug(
                        f"Processing Zigbee2MQTT bridge state message on topic: {topic}"
                    )
                    self._handle_zigbee2mqtt_state(payload)
                else:
                    # Handle general messages
                    logger.info(
                        f"📨 Processing general message on topic: {topic}"
                    )
                    logger.debug(
                        f"Processing general message on topic: {topic}"
                    )
                    self._handle_general_message(topic, payload)

                # Calculate processing duration
                processing_time = asyncio.get_event_loop().time() - start_time
                logger.debug(
                    f"Message processing completed in {processing_time:.4f}s"
                )
                self.metrics.observe_processing_duration(
                    topic, processing_time
                )

            except Exception as e:
                logger.error(
                    f"Error processing message from topic {topic}: {e}"
                )
                logger.debug(
                    f"Error details - payload_size: {len(payload)}, exception_type: {type(e).__name__}"
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
            logger.debug(
                f"Connection attempt details - client_id: {self.client_id}, credentials: {'yes' if self.username else 'no'}"
            )
            self.metrics.increment_connection_attempts()

            # FastMQTT connects automatically when integrated with FastAPI
            # We just need to mark as connected and let FastMQTT handle the rest
            logger.debug(
                "FastMQTT connects automatically - marking as connected"
            )
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
            logger.debug(f"Client info set: {client_info}")

            logger.info("Successfully connected to MQTT broker")
            logger.info(
                "🔍 FastMQTT will establish connection when FastAPI starts - monitoring for actual connection"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            logger.debug(
                f"Connection failure details - exception_type: {type(e).__name__}, exception_args: {e.args}"
            )
            self.metrics.increment_connection_failures(str(type(e).__name__))
            self.metrics.set_connection_status(False)
            return False

    async def disconnect(self):
        """Disconnect from the MQTT broker."""
        try:
            if self.connected:
                logger.debug("Initiating MQTT disconnect")
                # FastMQTT doesn't have a disconnect() method - it disconnects automatically
                # when the application shuts down. We just need to mark as disconnected.
                self.connected = False
                self.metrics.set_connection_status(False)
                logger.info("Disconnected from MQTT broker")
                logger.debug("MQTT disconnect completed successfully")
            else:
                logger.debug("Disconnect called but not connected - skipping")
        except Exception as e:
            logger.error(f"Error disconnecting from MQTT broker: {e}")
            logger.debug(
                f"Disconnect error details - exception_type: {type(e).__name__}, exception_args: {e.args}"
            )

    async def subscribe(self, topic: str) -> bool:
        """Subscribe to a topic."""
        try:
            logger.debug(f"Subscribe request for topic: {topic}")

            if not self.connected:
                logger.warning(
                    "Cannot subscribe: not connected to MQTT broker"
                )
                logger.debug(
                    f"Subscribe failed - connection status: {self.connected}"
                )
                return False

            logger.info(f"Subscribing to topic: {topic}")
            logger.debug(
                f"Subscription attempt - topic: {topic}, current subscriptions: {list(self.subscribed_topics)}"
            )
            self.metrics.increment_subscription_attempts(topic)

            # FastMQTT subscribe is not async
            logger.debug(f"Calling FastMQTT subscribe for topic: {topic}")
            self.mqtt.subscribe(topic)
            self.subscribed_topics.add(topic)

            # Update subscriptions count
            self.metrics.set_subscriptions_active(len(self.subscribed_topics))
            logger.debug(
                f"Subscription successful - topic: {topic}, total subscriptions: {len(self.subscribed_topics)}"
            )

            logger.info(f"Successfully subscribed to topic: {topic}")
            return True

        except Exception as e:
            logger.error(f"Failed to subscribe to topic {topic}: {e}")
            logger.debug(
                f"Subscription error details - topic: {topic}, exception_type: {type(e).__name__}, exception_args: {e.args}"
            )
            self.metrics.increment_subscription_failures(topic)
            return False

    async def publish(self, topic: str, message: str) -> bool:
        """Publish a message to a topic."""
        try:
            logger.debug(f"Publish request for topic: {topic}")

            if not self.connected:
                logger.warning("Cannot publish: not connected to MQTT broker")
                logger.debug(
                    f"Publish failed - connection status: {self.connected}"
                )
                return False

            message_size = len(message.encode("utf-8"))
            logger.debug(
                f"Publishing message to topic: {topic}, message_size: {message_size} bytes"
            )

            # Log message preview (first 200 chars for safety)
            message_preview = message[:200]
            if len(message) > 200:
                message_preview += "..."
            logger.debug(f"Message preview: {message_preview}")

            self.metrics.increment_messages_published(topic)
            self.metrics.observe_message_size(topic, message_size)

            # FastMQTT publish is not async
            logger.debug(f"Calling FastMQTT publish for topic: {topic}")
            self.mqtt.publish(topic, message)
            logger.debug(f"Successfully published message to topic: {topic}")
            return True

        except Exception as e:
            logger.error(f"Failed to publish message to topic {topic}: {e}")
            logger.debug(
                f"Publish error details - topic: {topic}, message_size: {len(message.encode('utf-8'))}, exception_type: {type(e).__name__}, exception_args: {e.args}"
            )
            return False

    def _handle_zigbee2mqtt_health(self, payload):
        """Handle Zigbee2MQTT health messages."""
        try:
            logger.debug(
                f"Processing Zigbee2MQTT health message - payload_size: {len(payload)} bytes"
            )

            # Decode payload
            if isinstance(payload, bytes):
                payload_str = payload.decode("utf-8")
                logger.debug("Payload was bytes, decoded to string")
            else:
                payload_str = str(payload)
                logger.debug("Payload was already string")

            # Log payload preview
            payload_preview = payload_str[:200]
            if len(payload_str) > 200:
                payload_preview += "..."
            logger.debug(f"Health payload preview: {payload_preview}")

            # Parse JSON
            logger.debug("Parsing health data as JSON")
            health_data = json.loads(payload_str)
            logger.debug(
                f"Health data parsed successfully - keys: {list(health_data.keys())}"
            )

            # Update Zigbee2MQTT metrics
            logger.debug("Updating Zigbee2MQTT health metrics")
            self.zigbee2mqtt_metrics.update_bridge_health(health_data)

            logger.debug("Updated Zigbee2MQTT health metrics successfully")

        except json.JSONDecodeError as e:
            logger.error(
                f"Failed to parse Zigbee2MQTT health data as JSON: {e}"
            )
            logger.debug(
                f"JSON parse error details - error_position: {e.pos}, error_line: {e.lineno}, error_column: {e.colno}"
            )
            self.metrics.increment_processing_errors(
                self.zigbee2mqtt_health_topic, "json_parse_error"
            )
        except Exception as e:
            logger.error(f"Error handling Zigbee2MQTT health message: {e}")
            logger.debug(
                f"Health message error details - exception_type: {type(e).__name__}, exception_args: {e.args}"
            )
            self.metrics.increment_processing_errors(
                self.zigbee2mqtt_health_topic, "handler_error"
            )

    def _handle_zigbee2mqtt_state(self, payload):
        """Handle Zigbee2MQTT bridge state messages."""
        try:
            logger.debug(
                f"Processing Zigbee2MQTT bridge state message - payload_size: {len(payload)} bytes"
            )

            # Decode payload
            if isinstance(payload, bytes):
                payload_str = payload.decode("utf-8")
                logger.debug("Payload was bytes, decoded to string")
            else:
                payload_str = str(payload)
                logger.debug("Payload was already string")

            # Log payload preview
            payload_preview = payload_str[:200]
            if len(payload_str) > 200:
                payload_preview += "..."
            logger.debug(f"State payload preview: {payload_preview}")

            # Parse JSON
            logger.debug("Parsing state data as JSON")
            state_data = json.loads(payload_str)
            logger.debug(
                f"State data parsed successfully - keys: {list(state_data.keys())}"
            )

            # Update Zigbee2MQTT metrics
            logger.debug("Updating Zigbee2MQTT state metrics")
            self.zigbee2mqtt_metrics.update_bridge_state(state_data)

            logger.debug("Updated Zigbee2MQTT state metrics successfully")

        except json.JSONDecodeError as e:
            logger.error(
                f"Failed to parse Zigbee2MQTT state data as JSON: {e}"
            )
            logger.debug(
                f"JSON parse error details - error_position: {e.pos}, error_line: {e.lineno}, error_column: {e.colno}"
            )
            self.metrics.increment_processing_errors(
                self.zigbee2mqtt_state_topic, "json_parse_error"
            )
        except Exception as e:
            logger.error(f"Error handling Zigbee2MQTT state message: {e}")
            logger.debug(
                f"State message error details - exception_type: {type(e).__name__}, exception_args: {e.args}"
            )
            self.metrics.increment_processing_errors(
                self.zigbee2mqtt_state_topic, "handler_error"
            )

    def _handle_general_message(self, topic: str, payload):
        """Handle general MQTT messages."""
        try:
            logger.debug(
                f"Processing general message - topic: {topic}, payload_size: {len(payload)} bytes"
            )

            # Decode payload
            if isinstance(payload, bytes):
                payload_str = payload.decode("utf-8")
                logger.debug(
                    "General message payload was bytes, decoded to string"
                )
            else:
                payload_str = str(payload)
                logger.debug("General message payload was already string")

            # Log payload preview
            payload_preview = payload_str[:200]
            if len(payload_str) > 200:
                payload_preview += "..."
            logger.debug(f"General message payload preview: {payload_preview}")

            # Try to parse as JSON
            try:
                logger.debug("Attempting to parse general message as JSON")
                data = json.loads(payload_str)
                logger.debug(
                    f"Successfully parsed JSON message on topic {topic} - keys: {list(data.keys()) if isinstance(data, dict) else 'not_dict'}"
                )
                logger.debug(f"JSON message content: {data}")
            except json.JSONDecodeError as json_error:
                logger.debug(f"General message is not JSON - topic: {topic}")
                logger.debug(f"Non-JSON message content: {payload_str}")
                logger.debug(
                    f"JSON parse error details - error_position: {json_error.pos}, error_line: {json_error.lineno}, error_column: {json_error.colno}"
                )

        except Exception as e:
            logger.error(
                f"Error handling general message from topic {topic}: {e}"
            )
            logger.debug(
                f"General message error details - topic: {topic}, payload_size: {len(payload)}, exception_type: {type(e).__name__}, exception_args: {e.args}"
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
