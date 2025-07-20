import os
import platform
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from prometheus_fastapi_instrumentator import Instrumentator

from app.logging_config import get_logger, setup_logging
from app.version import version

# Setup logging
setup_logging()
logger = get_logger(__name__)


# Create lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Ziggy API application")
    instrumentator.expose(app)
    logger.info("Prometheus metrics exposed")
    yield
    # Shutdown
    logger.info("Shutting down Ziggy API application")


# Create FastAPI app
app = FastAPI(
    title="Ziggy API",
    description="A FastAPI application with Prometheus metrics",
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
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "Ziggy API",
        "version": version,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "platform": platform.system(),
        "python_version": platform.python_version(),
    }


# Run the application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
