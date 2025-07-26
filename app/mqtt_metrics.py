from typing import Any, Dict

from prometheus_client import Counter, Gauge, Histogram, Info

# MQTT Connection Metrics
mqtt_connection_status = Gauge(
    "ziggy_mqtt_connection_status",
    "MQTT connection status (1=connected, 0=disconnected)",
    labelnames=["broker_host", "broker_port", "bridge_name"],
)

mqtt_connection_attempts = Counter(
    "ziggy_mqtt_connection_attempts_total",
    "Total number of MQTT connection attempts",
    labelnames=["broker_host", "broker_port", "bridge_name"],
)

mqtt_connection_failures = Counter(
    "ziggy_mqtt_connection_failures_total",
    "Total number of MQTT connection failures",
    labelnames=["broker_host", "broker_port", "reason", "bridge_name"],
)

# MQTT Message Metrics
mqtt_messages_received = Counter(
    "ziggy_mqtt_messages_received_total",
    "Total number of MQTT messages received",
    labelnames=["topic", "broker_host", "bridge_name"],
)

mqtt_messages_published = Counter(
    "ziggy_mqtt_messages_published_total",
    "Total number of MQTT messages published",
    labelnames=["topic", "broker_host", "bridge_name"],
)

mqtt_message_size_bytes = Histogram(
    "ziggy_mqtt_message_size_bytes",
    "Size of MQTT messages in bytes",
    labelnames=["topic", "broker_host", "bridge_name"],
    buckets=[10, 50, 100, 500, 1000, 5000, 10000],
)

# MQTT Processing Metrics
mqtt_message_processing_duration = Histogram(
    "ziggy_mqtt_message_processing_duration_seconds",
    "Time spent processing MQTT messages",
    labelnames=["topic", "broker_host", "bridge_name"],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0],
)

mqtt_message_processing_errors = Counter(
    "ziggy_mqtt_message_processing_errors_total",
    "Total number of MQTT message processing errors",
    labelnames=["topic", "broker_host", "error_type", "bridge_name"],
)

# MQTT Subscription Metrics
mqtt_subscriptions_active = Gauge(
    "ziggy_mqtt_subscriptions_active",
    "Number of active MQTT subscriptions",
    labelnames=["broker_host", "bridge_name"],
)

mqtt_subscription_attempts = Counter(
    "ziggy_mqtt_subscription_attempts_total",
    "Total number of MQTT subscription attempts",
    labelnames=["topic", "broker_host", "bridge_name"],
)

mqtt_subscription_failures = Counter(
    "ziggy_mqtt_subscription_failures_total",
    "Total number of MQTT subscription failures",
    labelnames=["topic", "broker_host", "bridge_name"],
)

# MQTT Client Info
mqtt_client_info = Info(
    "ziggy_mqtt_client",
    "MQTT client information",
    labelnames=["client_id", "broker_host", "broker_port", "bridge_name"],
)


class MQTTMetrics:
    """Class to manage MQTT-related Prometheus metrics."""

    def __init__(
        self,
        broker_host: str,
        broker_port: int,
        client_id: str,
        bridge_name: str = "default",
    ):
        """Initialize MQTT metrics with broker information."""
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client_id = client_id
        self.bridge_name = bridge_name
        self.labels = {
            "broker_host": broker_host,
            "broker_port": str(broker_port),
            "bridge_name": bridge_name,
        }

    def set_connection_status(self, connected: bool):
        """Update connection status metric."""
        mqtt_connection_status.labels(**self.labels).set(1 if connected else 0)

    def increment_connection_attempts(self):
        """Increment connection attempts counter."""
        mqtt_connection_attempts.labels(**self.labels).inc()

    def increment_connection_failures(self, reason: str = "unknown"):
        """Increment connection failures counter."""
        labels = {**self.labels, "reason": reason}
        mqtt_connection_failures.labels(**labels).inc()

    def increment_messages_received(self, topic: str):
        """Increment messages received counter."""
        labels = {
            "topic": topic,
            "broker_host": self.broker_host,
            "bridge_name": self.bridge_name,
        }
        mqtt_messages_received.labels(**labels).inc()

    def increment_messages_published(self, topic: str):
        """Increment messages published counter."""
        labels = {
            "topic": topic,
            "broker_host": self.broker_host,
            "bridge_name": self.bridge_name,
        }
        mqtt_messages_published.labels(**labels).inc()

    def observe_message_size(self, topic: str, size_bytes: int):
        """Observe message size histogram."""
        labels = {
            "topic": topic,
            "broker_host": self.broker_host,
            "bridge_name": self.bridge_name,
        }
        mqtt_message_size_bytes.labels(**labels).observe(size_bytes)

    def observe_processing_duration(self, topic: str, duration_seconds: float):
        """Observe message processing duration histogram."""
        labels = {
            "topic": topic,
            "broker_host": self.broker_host,
            "bridge_name": self.bridge_name,
        }
        mqtt_message_processing_duration.labels(**labels).observe(
            duration_seconds
        )

    def increment_processing_errors(self, topic: str, error_type: str):
        """Increment message processing errors counter."""
        labels = {
            "topic": topic,
            "broker_host": self.broker_host,
            "error_type": error_type,
            "bridge_name": self.bridge_name,
        }
        mqtt_message_processing_errors.labels(**labels).inc()

    def set_subscriptions_active(self, count: int):
        """Set active subscriptions gauge."""
        mqtt_subscriptions_active.labels(
            broker_host=self.broker_host, bridge_name=self.bridge_name
        ).set(count)

    def increment_subscription_attempts(self, topic: str):
        """Increment subscription attempts counter."""
        labels = {
            "topic": topic,
            "broker_host": self.broker_host,
            "bridge_name": self.bridge_name,
        }
        mqtt_subscription_attempts.labels(**labels).inc()

    def increment_subscription_failures(self, topic: str):
        """Increment subscription failures counter."""
        labels = {
            "topic": topic,
            "broker_host": self.broker_host,
            "bridge_name": self.bridge_name,
        }
        mqtt_subscription_failures.labels(**labels).inc()

    def set_client_info(self, info: Dict[str, Any]):
        """Set client information."""
        labels = {
            "client_id": self.client_id,
            "broker_host": self.broker_host,
            "broker_port": str(self.broker_port),
            "bridge_name": self.bridge_name,
        }
        # Filter out label keys from info to avoid conflicts
        info_without_labels = {
            k: v for k, v in info.items() if k not in labels
        }
        mqtt_client_info.labels(**labels).info(info_without_labels)

    def reset_connection_status(self):
        """Reset connection status to disconnected."""
        self.set_connection_status(False)


# Global metrics instance (will be set by the MQTT client)
mqtt_metrics: MQTTMetrics = None


def get_mqtt_metrics() -> MQTTMetrics:
    """Get the global MQTT metrics instance."""
    return mqtt_metrics


def set_mqtt_metrics(metrics: MQTTMetrics):
    """Set the global MQTT metrics instance."""
    global mqtt_metrics
    mqtt_metrics = metrics
