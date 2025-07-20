# Ziggy API

A FastAPI application with Prometheus metrics, health checks, comprehensive logging, and MQTT Zigbee integration.

## Features

- **FastAPI Web Framework**: Modern, fast web framework for building APIs
- **Prometheus Metrics**: Built-in metrics collection and exposure
- **Health Checks**: Detailed health endpoint with service status
- **Comprehensive Logging**: Configurable logging with multiple handlers and formats
- **MQTT Integration**: Subscribe to Zigbee topics using fastapi-mqtt
- **Docker Support**: Containerized application with health checks
- **Unit Tests**: Comprehensive test suite for all functionality

## Project Structure

```
ziggy/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── version.py           # Version information
│   ├── logging_config.py    # Logging configuration
│   └── mqtt_client.py       # MQTT client implementation
├── tests/
│   ├── __init__.py
│   ├── test_main.py         # Main application tests
│   ├── test_logging.py      # Logging configuration tests
│   └── test_mqtt.py         # MQTT client tests
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile              # Docker container definition
├── requirements.txt         # Python dependencies
├── prometheus.yml          # Prometheus configuration
└── README.md              # This file
```

## Quick Start

### Using Docker (Recommended)

1. **Clone and build the application:**

   ```bash
   git clone <repository-url>
   cd ziggy
   docker compose build
   ```

2. **Run the application:**

   ```bash
   docker compose up -d
   ```

3. **Check the application:**

   ```bash
   curl http://localhost:8000/health
   ```

### Local Development

1. **Set up a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run the application:**

   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Run tests:**

   ```bash
   python -m pytest tests/ -v
   ```

## API Endpoints

### Core Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check with detailed service status
- `GET /metrics` - Prometheus metrics

### MQTT Endpoints

- `GET /mqtt/status` - MQTT connection status and configuration
- `POST /mqtt/publish` - Publish a message to an MQTT topic

## Configuration

### Environment Variables

#### Logging Configuration

- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) - Default: INFO
- `LOG_FORMAT`: Log format (default, json, simple) - Default: default
- `LOG_HANDLERS`: Comma-separated list of handlers (console, file) - Default: console
- `LOG_FILE`: Log file path (for file handler) - Default: logs/app.log
- `LOG_MAX_BYTES`: Maximum log file size in bytes - Default: 10485760 (10MB)
- `LOG_BACKUP_COUNT`: Number of backup log files - Default: 5

#### MQTT Configuration

- `MQTT_ENABLED`: Enable MQTT client (true/false) - Default: false
- `MQTT_BROKER_HOST`: MQTT broker hostname - Default: localhost
- `MQTT_BROKER_PORT`: MQTT broker port - Default: 1883
- `MQTT_USERNAME`: MQTT broker username - Optional
- `MQTT_PASSWORD`: MQTT broker password - Optional
- `MQTT_ZIGBEE_TOPIC`: Zigbee topic to subscribe to - Default: zigbee2mqtt/#
- `MQTT_CLIENT_ID`: MQTT client ID - Default: ziggy-api
- `MQTT_KEEPALIVE`: MQTT keepalive interval in seconds - Default: 60

#### General Configuration

- `ENVIRONMENT`: Application environment (development, production) - Default: development

### Docker Configuration

The application includes a Docker Compose configuration with:

- **Service**: `ziggy` - The main application
- **Port**: `8000` - Exposed on host port 8000
- **Health Check**: Uses curl to check `/health` endpoint
- **Logging**: Configurable via environment variables
- **MQTT**: Configurable via environment variables

## MQTT Integration

The application includes a comprehensive MQTT client that can subscribe to Zigbee topics. The MQTT client is built using [fastapi-mqtt](https://github.com/sabuhish/fastapi-mqtt) for seamless integration with FastAPI.

### Features

- **Automatic Connection Management**: Handles connection, disconnection, and reconnection
- **Message Handlers**: Register custom handlers for specific topics or wildcard patterns
- **JSON Support**: Automatic JSON parsing of incoming messages
- **Error Handling**: Robust error handling for connection and message processing
- **Configuration**: Fully configurable via environment variables

### Usage

1. **Enable MQTT** by setting `MQTT_ENABLED=true`
2. **Configure broker** with `MQTT_BROKER_HOST` and optional credentials
3. **Customize topic** with `MQTT_ZIGBEE_TOPIC` (default: `zigbee2mqtt/#`)
4. **Add message handlers** in your application code

### Example Configuration

```bash
# Enable MQTT
export MQTT_ENABLED=true

# Configure broker
export MQTT_BROKER_HOST=your-mqtt-broker.com
export MQTT_BROKER_PORT=1883
export MQTT_USERNAME=your-username
export MQTT_PASSWORD=your-password

# Customize topic
export MQTT_ZIGBEE_TOPIC=zigbee2mqtt/#

# Optional: Customize client ID
export MQTT_CLIENT_ID=ziggy-api
```

### Message Handling

The application automatically handles incoming Zigbee messages and logs them. You can extend the message handling by modifying the `handle_zigbee_message` function in `app/main.py` or by adding custom handlers to the MQTT client.

## Logging

The application includes a comprehensive logging system with the following features:

### Logging Handlers

- **Console Handler**: Outputs logs to stdout/stderr
- **File Handler**: Writes logs to files with rotation
- **JSON Handler**: Outputs structured JSON logs

### Logging Formats

- **Default**: Human-readable format with timestamp, level, and message
- **JSON**: Structured JSON format for log aggregation
- **Simple**: Minimal format for quick debugging

### Configuration Examples

```bash
# Console logging only (default)
export LOG_HANDLERS=console
export LOG_LEVEL=INFO

# File logging with rotation
export LOG_HANDLERS=file
export LOG_FILE=logs/app.log
export LOG_MAX_BYTES=10485760
export LOG_BACKUP_COUNT=5

# Both console and file logging
export LOG_HANDLERS=console,file
export LOG_FORMAT=json
```

## Health Checks

The application includes a comprehensive health check endpoint at `/health` that provides:

- **Service Status**: Overall health status
- **Timestamp**: Current UTC timestamp
- **Version Information**: Application version
- **Environment**: Current environment
- **Platform Information**: OS and Python version
- **MQTT Status**: MQTT connection status and configuration

### Health Check Response

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000000+00:00",
  "service": "Ziggy API",
  "version": "0.2.0",
  "environment": "production",
  "platform": "Linux",
  "python_version": "3.11.0",
  "mqtt": {
    "status": "connected",
    "info": {
      "connected": true,
      "broker_host": "localhost",
      "broker_port": 1883,
      "topic": "zigbee2mqtt/#",
      "client_id": "ziggy-api",
      "has_credentials": false
    }
  }
}
```

## Testing

The application includes comprehensive unit tests for all functionality:

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_mqtt.py -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

### Test Categories

- **Main Application Tests**: Endpoint functionality, response formats
- **Logging Tests**: Configuration, environment variables, error handling
- **MQTT Tests**: Client initialization, message handling, connection management

## Docker Commands

### Building and Running

```bash
# Build the image
docker compose build

# Run the application
docker compose up -d

# View logs
docker compose logs -f ziggy

# Stop the application
docker compose down
```

### Health Check

The Docker container includes a health check that:

- Uses `curl` to check the `/health` endpoint
- Runs every 30 seconds
- Has a 10-second timeout
- Requires 3 consecutive failures to mark as unhealthy

### Environment Variables

You can override environment variables in `docker-compose.yml` or by creating a `.env` file:

```bash
# Example .env file
ENVIRONMENT=production
LOG_LEVEL=INFO
MQTT_ENABLED=true
MQTT_BROKER_HOST=your-broker.com
MQTT_USERNAME=your-username
MQTT_PASSWORD=your-password
```

## Development

### Code Quality

The project uses several tools for code quality:

- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Linting
- **pre-commit**: Git hooks for code quality

### Pre-commit Setup

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

## Monitoring

### Prometheus Metrics

The application exposes Prometheus metrics at `/metrics` including:

- HTTP request metrics
- Application-specific metrics
- System metrics

### Log Monitoring

Logs can be monitored through:

- **Console output**: For development
- **File logs**: For production with rotation
- **JSON format**: For log aggregation systems

## Troubleshooting

### Common Issues

1. **MQTT Connection Failed**
   - Check `MQTT_BROKER_HOST` and `MQTT_BROKER_PORT`
   - Verify credentials if authentication is required
   - Ensure the MQTT broker is running and accessible

2. **Logging Issues**
   - Check `LOG_LEVEL` and `LOG_HANDLERS` configuration
   - Ensure log directory exists for file logging
   - Verify file permissions for log files

3. **Health Check Failing**
   - Check application logs for errors
   - Verify all required environment variables are set
   - Ensure the application is responding on port 8000

### Debug Mode

Enable debug logging for troubleshooting:

```bash
export LOG_LEVEL=DEBUG
export LOG_HANDLERS=console
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License.
