import os
import platform
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.version import version


# Create lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    instrumentator.expose(app)
    yield
    # Shutdown (if needed)


# Create FastAPI app
app = FastAPI(
    title="Ziggy API",
    description="A FastAPI application with Prometheus metrics",
    version=version,
    lifespan=lifespan,
)

# Initialize and configure Prometheus instrumentator
instrumentator = Instrumentator().instrument(app)


# Define routes
@app.get("/")
async def root():
    return {"message": "Welcome to Ziggy API"}


@app.get("/health")
async def health_check():
    """Health check endpoint that returns detailed service status."""
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
