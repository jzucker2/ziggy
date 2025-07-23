import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.app_metrics import get_app_info, update_app_info
from app.logging_config import setup_logging
from app.mqtt_client import ZiggyMQTTClient
from app.mqtt_metrics import get_mqtt_metrics
from app.version import __version__
from app.zigbee2mqtt_metrics import (
    Zigbee2MQTTMetrics,
    get_zigbee2mqtt_metrics,
    set_zigbee2mqtt_metrics,
)

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)


# Global variables for MQTT client and metrics
mqtt_client: Optional[ZiggyMQTTClient] = None
zigbee2mqtt_metrics: Optional[Zigbee2MQTTMetrics] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("🚀 Starting Ziggy application...")

    # Initialize MQTT client
    global mqtt_client
    mqtt_client = await initialize_mqtt_client()

    # Initialize FastMQTT with FastAPI app if client is available
    if mqtt_client and mqtt_client.mqtt:
        logger.info("🔌 Initializing FastMQTT with FastAPI app")
        mqtt_client.mqtt.init_app(app)

        # Try to establish connection
        try:
            logger.info("🔌 Attempting to connect FastMQTT client")
            await mqtt_client.mqtt.connection()
            logger.info("✅ FastMQTT client connected successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect FastMQTT client: {e}")

    # Initialize Zigbee2MQTT metrics
    global zigbee2mqtt_metrics
    zigbee2mqtt_metrics = Zigbee2MQTTMetrics(
        bridge_name=os.getenv("ZIGBEE2MQTT_BRIDGE_NAME", "navi"),
        base_topic=os.getenv("ZIGBEE2MQTT_BASE_TOPIC", "zigbee2mqtt"),
    )
    set_zigbee2mqtt_metrics(zigbee2mqtt_metrics)

    # Set application info metrics
    app_info = get_app_info()
    update_app_info(app_info)
    logger.info(
        f"📊 Set application info metrics - version: {app_info['version']}"
    )

    logger.info("✅ Ziggy application started successfully")

    yield

    # Shutdown
    logger.info("🛑 Shutting down Ziggy application...")

    # Disconnect MQTT client
    if mqtt_client:
        await mqtt_client.disconnect()

    logger.info("✅ Ziggy application shutdown complete")


async def initialize_mqtt_client() -> ZiggyMQTTClient:
    """Initialize the MQTT client."""
    # Check if MQTT is enabled (defaults to true)
    if os.getenv("MQTT_ENABLED", "true").lower() != "true":
        logger.info("MQTT client disabled via environment variable")
        return None

    # Check if broker host is configured
    broker_host = os.getenv("MQTT_BROKER_HOST")
    if not broker_host:
        logger.info(
            "MQTT broker host not configured, skipping MQTT client initialization"
        )
        return None

    try:
        client = ZiggyMQTTClient()

        # FastMQTT connects automatically when integrated with FastAPI
        # We just need to mark as connected and set up subscriptions
        logger.info("🔌 Initializing MQTT client with FastMQTT")
        logger.debug("Initializing MQTT client with FastMQTT")

        # Mark as connected (FastMQTT will handle actual connection)
        client.connected = True
        client.metrics.set_connection_status(True)

        # Set client info
        client_info = {
            "connected": "true",
            "client_id": client.client_id,
            "broker_host": client.broker_host,
            "broker_port": str(client.broker_port),
            "has_credentials": (
                "true" if client.username and client.password else "false"
            ),
        }
        client.metrics.set_client_info(client_info)

        # Add the health topic to subscribed_topics - the on_connect handler will subscribe when connected
        logger.info(
            f"📡 Adding subscription for topic: {client.zigbee2mqtt_health_topic}"
        )
        logger.debug(
            f"Adding subscription for topic: {client.zigbee2mqtt_health_topic}"
        )
        client.subscribed_topics.add(client.zigbee2mqtt_health_topic)

        # Add the state topic to subscribed_topics
        logger.info(
            f"📡 Adding subscription for topic: {client.zigbee2mqtt_state_topic}"
        )
        logger.debug(
            f"Adding subscription for topic: {client.zigbee2mqtt_state_topic}"
        )
        client.subscribed_topics.add(client.zigbee2mqtt_state_topic)

        # Add the info topic to subscribed_topics
        logger.info(
            f"📡 Adding subscription for topic: {client.zigbee2mqtt_info_topic}"
        )
        logger.debug(
            f"Adding subscription for topic: {client.zigbee2mqtt_info_topic}"
        )
        client.subscribed_topics.add(client.zigbee2mqtt_info_topic)

        client.metrics.set_subscriptions_active(len(client.subscribed_topics))

        logger.info("✅ MQTT client initialized successfully")
        logger.debug(
            f"MQTT client ready - broker: {client.broker_host}:{client.broker_port}, subscriptions: {list(client.subscribed_topics)}"
        )
        return client

    except Exception as e:
        logger.error(f"Error initializing MQTT client: {e}")
        logger.debug(
            f"MQTT initialization error details - exception_type: {type(e).__name__}, exception_args: {e.args}"
        )
        return None


async def cleanup_mqtt_client():
    """Clean up the MQTT client."""
    global mqtt_client
    if mqtt_client:
        await mqtt_client.disconnect()
        mqtt_client = None
        logger.info("MQTT client cleaned up")


# Create FastAPI app
app = FastAPI(
    title="Ziggy API",
    description="A FastAPI application for Zigbee device management with MQTT integration",
    version=__version__,
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    logger.info(f"Request: {request.method} {request.url.path}")
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")

    return response


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Ziggy API",
        "version": __version__,
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    import platform
    import sys

    return {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
        },
        "python": {
            "version": sys.version,
            "implementation": platform.python_implementation(),
        },
        "mqtt": {
            "enabled": mqtt_client is not None,
            "connected": mqtt_client.connected if mqtt_client else False,
        },
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.get("/mqtt/status")
async def mqtt_status():
    """Get MQTT connection status."""
    if not mqtt_client:
        return {
            "enabled": False,
            "message": "MQTT client not initialized (disabled or configuration missing)",
        }

    return {
        "enabled": True,
        "connected": mqtt_client.connected,
        "connection_info": mqtt_client.get_connection_info(),
    }


@app.get("/mqtt/metrics")
async def mqtt_metrics():
    """Get MQTT-specific metrics information."""
    metrics = get_mqtt_metrics()
    if not metrics:
        return {
            "enabled": False,
            "message": "MQTT metrics not available. MQTT client not initialized.",
        }

    return {
        "enabled": True,
        "metrics_info": {
            "broker_host": metrics.broker_host,
            "broker_port": metrics.broker_port,
            "client_id": metrics.client_id,
            "available_metrics": [
                "ziggy_mqtt_connection_status",
                "ziggy_mqtt_connection_attempts_total",
                "ziggy_mqtt_connection_failures_total",
                "ziggy_mqtt_messages_received_total",
                "ziggy_mqtt_messages_published_total",
                "ziggy_mqtt_message_size_bytes",
                "ziggy_mqtt_message_processing_duration_seconds",
                "ziggy_mqtt_message_processing_errors_total",
                "ziggy_mqtt_subscriptions_active",
                "ziggy_mqtt_subscription_attempts_total",
                "ziggy_mqtt_subscription_failures_total",
                "ziggy_mqtt_client_info",
            ],
        },
    }


@app.get("/zigbee2mqtt/metrics")
async def get_zigbee2mqtt_metrics_endpoint():
    """Get Zigbee2MQTT-specific metrics information."""
    metrics = get_zigbee2mqtt_metrics()
    if not metrics:
        return {
            "enabled": False,
            "message": "Zigbee2MQTT metrics not available. MQTT client not initialized.",
        }

    return {
        "enabled": True,
        "metrics_info": {
            "bridge_name": metrics.bridge_name,
            "available_metrics": [
                "ziggy_zigbee2mqtt_bridge_health_timestamp",
                "ziggy_zigbee2mqtt_os_load_average_1m",
                "ziggy_zigbee2mqtt_os_load_average_5m",
                "ziggy_zigbee2mqtt_os_load_average_15m",
                "ziggy_zigbee2mqtt_os_memory_used_mb",
                "ziggy_zigbee2mqtt_os_memory_percent",
                "ziggy_zigbee2mqtt_process_uptime_seconds",
                "ziggy_zigbee2mqtt_process_memory_used_mb",
                "ziggy_zigbee2mqtt_process_memory_percent",
                "ziggy_zigbee2mqtt_mqtt_connected",
                "ziggy_zigbee2mqtt_mqtt_queued_messages",
                "ziggy_zigbee2mqtt_mqtt_published_messages_total",
                "ziggy_zigbee2mqtt_mqtt_received_messages_total",
                "ziggy_zigbee2mqtt_device_leave_count",
                "ziggy_zigbee2mqtt_device_network_address_changes",
                "ziggy_zigbee2mqtt_device_appearances_total",
                "ziggy_zigbee2mqtt_bridge_state",
                "ziggy_zigbee2mqtt_bridge_state_timestamp",
                "ziggy_zigbee2mqtt_bridge_info_version",
                "ziggy_zigbee2mqtt_bridge_info_coordinator",
                "ziggy_zigbee2mqtt_bridge_info_config",
                "ziggy_zigbee2mqtt_bridge_info_timestamp",
                "ziggy_app_info",
            ],
        },
    }


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "path": request.url.path},
    )


@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc):
    """Handle 405 errors."""
    return JSONResponse(
        status_code=405,
        content={
            "error": "Method not allowed",
            "method": request.method,
            "path": request.url.path,
        },
    )
