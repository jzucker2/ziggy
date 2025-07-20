import os
import platform
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from prometheus_fastapi_instrumentator import Instrumentator

from app.logging_config import get_logger, setup_logging
from app.mqtt_client import cleanup_mqtt_client, initialize_mqtt_client
from app.version import version

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Global MQTT client
mqtt_client = None


# Create lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global mqtt_client
    logger.info("Starting Ziggy API application")

    # Initialize MQTT client
    mqtt_client = await initialize_mqtt_client()
    if mqtt_client:
        # Add a default message handler for all Zigbee messages
        mqtt_client.add_message_handler("*", handle_zigbee_message)
        logger.info("MQTT client initialized and message handler added")
    else:
        logger.info(
            "MQTT client not initialized (disabled or configuration missing)"
        )

    instrumentator.expose(app)
    logger.info("Prometheus metrics exposed")
    yield

    # Shutdown
    logger.info("Shutting down Ziggy API application")
    await cleanup_mqtt_client()


# Create FastAPI app
app = FastAPI(
    title="Ziggy API",
    description="A FastAPI application with Prometheus metrics and MQTT Zigbee integration",
    version=version,
    lifespan=lifespan,
)

# Initialize and configure Prometheus instrumentator
instrumentator = Instrumentator().instrument(app)


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = datetime.now()

    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Log response
    process_time = datetime.now() - start_time
    logger.info(
        f"Response: {response.status_code} - {process_time.total_seconds():.3f}s"
    )

    return response


# MQTT message handler
async def handle_zigbee_message(topic: str, data):
    """Handle incoming Zigbee messages from MQTT."""
    logger.info(f"Processing Zigbee message from {topic}: {data}")

    # Here you can add specific logic for handling different types of Zigbee messages
    # For example, you could:
    # - Store messages in a database
    # - Trigger webhooks
    # - Update device states
    # - Send notifications

    # For now, we'll just log the message
    if isinstance(data, dict):
        # Handle structured data
        device_id = data.get("device_id", "unknown")
        state = data.get("state", "unknown")
        logger.info(f"Device {device_id} state: {state}")
    else:
        # Handle raw data
        logger.info(f"Raw Zigbee data: {data}")


# Define routes
@app.get("/")
async def root():
    """Root endpoint that returns a welcome message."""
    logger.debug("Root endpoint accessed")
    return {"message": "Welcome to Ziggy API"}


@app.get("/health")
async def health_check():
    """Health check endpoint that returns detailed service status."""
    logger.debug("Health check endpoint accessed")

    # Get MQTT connection status
    mqtt_status = "disabled"
    mqtt_info = {}
    if mqtt_client:
        mqtt_status = (
            "connected" if mqtt_client.is_connected() else "disconnected"
        )
        mqtt_info = mqtt_client.get_connection_info()

    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "Ziggy API",
        "version": version,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "mqtt": {"status": mqtt_status, "info": mqtt_info},
    }


@app.get("/mqtt/status")
async def mqtt_status():
    """Get MQTT connection status and configuration."""
    if not mqtt_client:
        return {
            "enabled": False,
            "message": "MQTT client not initialized. Set MQTT_ENABLED=true to enable.",
        }

    return {
        "enabled": True,
        "connected": mqtt_client.is_connected(),
        "connection_info": mqtt_client.get_connection_info(),
    }


@app.post("/mqtt/publish")
async def publish_message(topic: str, message: str):
    """Publish a message to an MQTT topic."""
    if not mqtt_client:
        return {"error": "MQTT client not initialized"}

    if not mqtt_client.is_connected():
        return {"error": "MQTT client not connected"}

    success = mqtt_client.publish(topic, message)
    return {"success": success, "topic": topic, "message": message}


# Run the application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
