# Ziggy - FastAPI with Prometheus Metrics

A FastAPI application with Docker containerization and Prometheus metrics integration using [prometheus-fastapi-instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator).

## Features

- FastAPI application with health check endpoint
- Prometheus metrics integration
- Docker containerization with built-in healthcheck
- Docker Compose setup for easy deployment
- Comprehensive unit tests
- Modern FastAPI lifespan event handlers

## Project Structure

```
ziggy/
├── app/                    # Application code
│   ├── __init__.py
│   ├── main.py            # FastAPI application
│   └── version.py         # Version information
├── tests/                  # Test files
│   ├── __init__.py
│   ├── conftest.py        # Test fixtures
│   └── test_main.py       # Unit tests
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile             # Docker configuration with healthcheck
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
└── README.md             # This file
```

## Requirements

- Docker and Docker Compose
- Python 3.13+ (for local development)

## Quick Start

### Using Docker Compose (Recommended)

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/ziggy.git
   cd ziggy
   ```

2. Start the application with Docker Compose:

   ```bash
   docker compose up -d
   ```

3. Access the application:
   - FastAPI application: <http://localhost:8000>
   - API documentation: <http://localhost:8000/docs>
   - Health check: <http://localhost:8000/health>
   - Metrics endpoint: <http://localhost:8000/metrics>

### Local Development

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```

2. Run the application:

   ```bash
   uvicorn app.main:app --reload
   ```

3. Access the application at <http://localhost:8000>

## Health Check

The application includes a comprehensive health check endpoint at `/health` that provides detailed service information:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.123456+00:00",
  "service": "Ziggy API",
  "version": "0.2.0",
  "environment": "development",
  "platform": "Linux",
  "python_version": "3.13.0"
}
```

### Docker Healthcheck

The Docker container includes a built-in healthcheck that:

- Runs every 30 seconds
- Times out after 10 seconds
- Has a 5-second start period
- Retries up to 3 times
- Uses curl to check the `/health` endpoint

You can check the health status with:

```bash
docker ps  # Shows health status
docker inspect <container_id>  # Shows detailed health info
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Run tests with verbose output
pytest -v

# Run only health check tests
pytest tests/test_main.py::TestHealthEndpoint -v
```

## API Endpoints

- `GET /`: Root endpoint that returns a welcome message
- `GET /health`: Health check endpoint with detailed service information
- `GET /metrics`: Prometheus metrics endpoint

## Monitoring with Prometheus

The application exposes Prometheus-compatible metrics at the `/metrics` endpoint. You can:

- **View metrics directly**: Visit <http://localhost:8000/metrics> to see the raw metrics
- **Integrate with external Prometheus**: Point your Prometheus server to `http://localhost:8000/metrics`
- **Use with Grafana**: Configure Grafana to read metrics from your app's metrics endpoint

Common metrics include:

- HTTP request count
- HTTP request duration
- HTTP request size
- HTTP response size

## Docker Commands

### Start the application

```bash
docker compose up -d
```

### Stop the application

```bash
docker compose down
```

### View logs

```bash
docker compose logs -f app
```

### Rebuild and restart

```bash
docker compose up -d --build
```

### Check container health

```bash
docker ps
docker inspect <container_id>
```

## Development

### Code Quality

The project includes several tools for maintaining code quality:

- **Black**: Code formatting
- **Flake8**: Linting
- **Pytest**: Testing framework
- **Pre-commit**: Git hooks for code quality

### Running Quality Checks

```bash
# Format code
black app/ tests/

# Lint code
flake8 app/ tests/

# Run all checks
make check
```

## License

MIT
