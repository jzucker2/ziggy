import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.logging_config import setup_logging
from app.mqtt_client import ZiggyMQTTClient
from app.mqtt_metrics import get_mqtt_metrics
from app.zigbee2mqtt_metrics import get_zigbee2mqtt_metrics

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

# Global MQTT client instance
mqtt_client: ZiggyMQTTClient = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Ziggy API application")

    # Log the configured log level and other logging settings
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_format = os.getenv("LOG_FORMAT", "default")
    log_handlers = os.getenv("LOG_HANDLERS", "console")
    logger.info(f"📊 Log level configured: {log_level}")
    logger.info(f"📝 Log format: {log_format}")
    logger.info(f"🖨️ Log handlers: {log_handlers}")
    logger.debug(f"Log level environment variable: {log_level}")
    logger.debug(f"Log format environment variable: {log_format}")
    logger.debug(f"Log handlers environment variable: {log_handlers}")

    # Initialize MQTT client
    global mqtt_client
    mqtt_client = await initialize_mqtt_client()

    # If MQTT client is initialized, integrate it with FastAPI
    if mqtt_client:
        # FastMQTT needs to be integrated with the FastAPI app
        logger.info("🔌 Integrating FastMQTT with FastAPI application")
        mqtt_client.mqtt.init_app(app)
        logger.info("✅ FastMQTT integrated with FastAPI application")

        # Try to explicitly start the FastMQTT client
        try:
            logger.info("🔌 Attempting to start FastMQTT client...")
            # FastMQTT might need explicit startup
            if hasattr(mqtt_client.mqtt, "mqtt_startup"):
                await mqtt_client.mqtt.mqtt_startup()
                logger.info("✅ FastMQTT client started explicitly")
            else:
                logger.info(
                    "⚠️ FastMQTT client doesn't have mqtt_startup method"
                )
        except Exception as e:
            logger.warning(f"⚠️ Failed to explicitly start FastMQTT: {e}")
    else:
        logger.info("⚠️ MQTT client not initialized - no FastMQTT integration")

    logger.info("Prometheus metrics exposed")
    yield

    # Shutdown
    logger.info("Shutting down Ziggy API application")
    if mqtt_client:
        await cleanup_mqtt_client()


async def initialize_mqtt_client() -> ZiggyMQTTClient:
    """Initialize and return the MQTT client."""
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
    version="1.0.0",
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
        "version": "1.0.0",
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
async def zigbee2mqtt_metrics():
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
                "ziggy_zigbee2mqtt_device_messages",
                "ziggy_zigbee2mqtt_device_messages_per_sec",
                "ziggy_zigbee2mqtt_device_appearances_total",
                "ziggy_zigbee2mqtt_bridge_info",
                "ziggy_zigbee2mqtt_base_topic_info",
                "ziggy_zigbee2mqtt_bridge_state",
                "ziggy_zigbee2mqtt_bridge_state_timestamp",
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
