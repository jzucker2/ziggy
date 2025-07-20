# Ziggy - FastAPI with Prometheus Metrics

A FastAPI application with Docker containerization and Prometheus metrics integration using [prometheus-fastapi-instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator).

## Features

- FastAPI application with health check endpoint
- Prometheus metrics integration
- Docker containerization
- Docker Compose setup for easy deployment

## Requirements

- Docker and Docker Compose
- Python 3.11+ (for local development)

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
   - FastAPI application: http://localhost:8000
   - API documentation: http://localhost:8000/docs
   - Metrics endpoint: http://localhost:8000/metrics

### Local Development

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

3. Access the application at http://localhost:8000

## API Endpoints

- `GET /`: Root endpoint that returns a welcome message
- `GET /health`: Health check endpoint
- `GET /metrics`: Prometheus metrics endpoint

## Monitoring with Prometheus

The application exposes Prometheus-compatible metrics at the `/metrics` endpoint. You can:

- **View metrics directly**: Visit http://localhost:8000/metrics to see the raw metrics
- **Integrate with external Prometheus**: Point your Prometheus server to `http://localhost:8000/metrics`
- **Use with Grafana**: Configure Grafana to read metrics from your app's metrics endpoint

Common metrics include:
- HTTP request count
- HTTP request duration
- HTTP request size
- HTTP response size

## Docker Commands

### Start the application:
```bash
docker compose up -d
```

### Stop the application:
```bash
docker compose down
```

### View logs:
```bash
docker compose logs -f app
```

### Rebuild and restart:
```bash
docker compose up -d --build
```

## License

MIT
