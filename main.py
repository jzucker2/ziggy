from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

# Create FastAPI app
app = FastAPI(
    title="Ziggy API",
    description="A FastAPI application with Prometheus metrics",
    version="0.1.0"
)

# Initialize and configure Prometheus instrumentator
instrumentator = Instrumentator().instrument(app)

# Register Prometheus metrics endpoint
@app.on_event("startup")
async def startup():
    instrumentator.expose(app)

# Define routes
@app.get("/")
async def root():
    return {"message": "Welcome to Ziggy API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)