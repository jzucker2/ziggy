# Ziggy API

A FastAPI application for Zigbee device management with MQTT integration and comprehensive Prometheus metrics.

## Features

- **FastAPI REST API** with health checks and metrics endpoints
- **MQTT Integration** using fastapi-mqtt for Zigbee2MQTT communication
- **Prometheus Metrics** for both MQTT and Zigbee2MQTT health monitoring
- **Comprehensive Logging** with configurable levels and formats
- **Docker Support** for easy deployment
- **Extensive Testing** with pytest

## Quick Start

### Prerequisites

- Python 3.8+
- MQTT Broker (e.g., Mosquitto)
- Zigbee2MQTT (optional, for Zigbee device management)

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd ziggy
   ```

2. **Create and activate virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   ```bash
   # Copy example environment file
   cp .env.example .env

   # Edit .env with your configuration
   nano .env
   ```

5. **Run the application:**

   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Configuration

### Environment Variables

#### MQTT Configuration

```bash
# Enable MQTT (required)
MQTT_ENABLED=true

# MQTT Broker Settings
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=your_username
MQTT_PASSWORD=your_password
MQTT_CLIENT_ID=ziggy-api

# MQTT Topics
ZIGBEE2MQTT_HEALTH_TOPIC=zigbee2mqtt/bridge/health
ZIGBEE2MQTT_BRIDGE_NAME=my-bridge
```

#### Logging Configuration

```bash
# Logging Level
LOG_LEVEL=INFO

# Logging Format
LOG_FORMAT=detailed  # simple, detailed, json

# Logging Handlers
LOG_HANDLERS=console,file  # console, file, or both
```

### Zigbee2MQTT Setup

To enable Zigbee2MQTT health monitoring, ensure your Zigbee2MQTT configuration includes:

```yaml
# Zigbee2MQTT configuration.yaml
mqtt:
  server: mqtt://localhost:1883
  user: your_username
  pass: your_password

# Enable health monitoring
health_check:
  enabled: true
  topic: zigbee2mqtt/bridge/health
```

## API Endpoints

### Core Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check with system status
- `GET /metrics` - Prometheus metrics endpoint

### MQTT Endpoints

- `GET /mqtt/status` - MQTT connection status and configuration
- `GET /mqtt/metrics` - MQTT-specific metrics information

### Zigbee2MQTT Endpoints

- `GET /zigbee2mqtt/metrics` - Zigbee2MQTT health metrics information

## Prometheus Metrics

### MQTT Metrics

All MQTT metrics are prefixed with `ziggy_mqtt_`:

#### Connection Metrics

- `ziggy_mqtt_connection_status` - Connection status (1=connected, 0=disconnected)
- `ziggy_mqtt_connection_attempts_total` - Total connection attempts
- `ziggy_mqtt_connection_failures_total` - Total connection failures

#### Message Metrics

- `ziggy_mqtt_messages_received_total` - Total messages received
- `ziggy_mqtt_messages_published_total` - Total messages published
- `ziggy_mqtt_message_size_bytes` - Message size distribution
- `ziggy_mqtt_message_processing_duration_seconds` - Message processing time

#### Subscription Metrics

- `ziggy_mqtt_subscriptions_active` - Number of active subscriptions
- `ziggy_mqtt_subscription_attempts_total` - Total subscription attempts
- `ziggy_mqtt_subscription_failures_total` - Total subscription failures

### Zigbee2MQTT Metrics

All Zigbee2MQTT metrics are prefixed with `ziggy_zigbee2mqtt_`:

#### Bridge Health Metrics

- `ziggy_zigbee2mqtt_bridge_health_timestamp` - Last health check timestamp

#### OS Metrics

- `ziggy_zigbee2mqtt_os_load_average_1m` - 1-minute CPU load average
- `ziggy_zigbee2mqtt_os_load_average_5m` - 5-minute CPU load average
- `ziggy_zigbee2mqtt_os_load_average_15m` - 15-minute CPU load average
- `ziggy_zigbee2mqtt_os_memory_used_mb` - Used memory in MB
- `ziggy_zigbee2mqtt_os_memory_percent` - Used memory percentage

#### Process Metrics

- `ziggy_zigbee2mqtt_process_uptime_seconds` - Zigbee2MQTT uptime
- `ziggy_zigbee2mqtt_process_memory_used_mb` - Process memory usage in MB
- `ziggy_zigbee2mqtt_process_memory_percent` - Process memory percentage

#### MQTT Metrics

- `ziggy_zigbee2mqtt_mqtt_connected` - MQTT connection status
- `ziggy_zigbee2mqtt_mqtt_queued_messages` - Queued messages count
- `ziggy_zigbee2mqtt_mqtt_published_messages_total` - Total published messages
- `ziggy_zigbee2mqtt_mqtt_received_messages_total` - Total received messages

#### Device Metrics

- `ziggy_zigbee2mqtt_device_leave_count` - Current device leave events
- `ziggy_zigbee2mqtt_device_network_address_changes` - Current network address changes
- `ziggy_zigbee2mqtt_device_messages` - Current device messages
- `ziggy_zigbee2mqtt_device_messages_per_sec` - Current messages per second per device
- `ziggy_zigbee2mqtt_device_appearances_total` - Total times device appeared in health messages

## Docker Deployment

### Using Docker Compose

1. **Create docker-compose.yml:**

   ```yaml
   version: '3.8'
   services:
     ziggy:
       build: .
       ports:
         - "8000:8000"
       environment:
         - MQTT_ENABLED=true
         - MQTT_BROKER_HOST=mqtt-broker
         - MQTT_BROKER_PORT=1883
         - MQTT_USERNAME=your_username
         - MQTT_PASSWORD=your_password
       depends_on:
         - mqtt-broker

     mqtt-broker:
       image: eclipse-mosquitto:latest
       ports:
         - "1883:1883"
       volumes:
         - ./mosquitto.conf:/mosquitto/config/mosquitto.conf
   ```

2. **Run with Docker Compose:**

   ```bash
   docker-compose up -d
   ```

### Using Docker

1. **Build the image:**

   ```bash
   docker build -t ziggy-api .
   ```

2. **Run the container:**

   ```bash
   docker run -d \
     --name ziggy-api \
     -p 8000:8000 \
     -e MQTT_ENABLED=true \
     -e MQTT_BROKER_HOST=your-mqtt-host \
     -e MQTT_BROKER_PORT=1883 \
     -e MQTT_USERNAME=your_username \
     -e MQTT_PASSWORD=your_password \
     ziggy-api
   ```

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_mqtt_metrics.py -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

### Code Quality

```bash
# Linting
flake8 app/ tests/ --max-line-length=88 --extend-ignore=E203,W503

# Formatting
black app/ tests/

# Type checking
mypy app/
```

### Project Structure

```
ziggy/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── mqtt_client.py       # MQTT client implementation
│   ├── mqtt_metrics.py      # MQTT Prometheus metrics
│   ├── zigbee2mqtt_metrics.py  # Zigbee2MQTT health metrics
│   └── logging_config.py    # Logging configuration
├── tests/
│   ├── __init__.py
│   ├── test_main.py         # API endpoint tests
│   ├── test_mqtt.py         # MQTT client tests
│   ├── test_mqtt_metrics.py # MQTT metrics tests
│   ├── test_zigbee2mqtt_metrics.py  # Zigbee2MQTT metrics tests
│   └── test_logging.py      # Logging tests
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose setup
├── prometheus.yml           # Prometheus configuration
└── README.md               # This file
```

## Monitoring and Alerting

### Prometheus Configuration

Add to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'ziggy-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### Grafana Dashboards

Create dashboards for:

- **MQTT Connection Health** - Monitor connection status and message flow
- **Zigbee2MQTT Bridge Health** - Monitor bridge performance and device activity
- **System Resources** - Monitor OS and process metrics

### Alerting Rules

Example Prometheus alerting rules:

```yaml
groups:
  - name: zigbee2mqtt-alerts
    rules:
      - alert: Zigbee2MQTTBridgeDown
        expr: ziggy_zigbee2mqtt_mqtt_connected == 0
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Zigbee2MQTT bridge is disconnected"

      - alert: HighMemoryUsage
        expr: ziggy_zigbee2mqtt_os_memory_percent > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
```
