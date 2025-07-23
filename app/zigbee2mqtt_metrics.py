from typing import Any, Dict, Optional

from prometheus_client import Counter, Gauge, Info

# Zigbee2MQTT Bridge Health Metrics
zigbee2mqtt_bridge_health_timestamp = Gauge(
    "ziggy_zigbee2mqtt_bridge_health_timestamp",
    "Timestamp of the last Zigbee2MQTT bridge health check",
    labelnames=["bridge_name"],
)

# OS Metrics
zigbee2mqtt_os_load_average_1m = Gauge(
    "ziggy_zigbee2mqtt_os_load_average_1m",
    "1-minute CPU load average",
    labelnames=["bridge_name"],
)

zigbee2mqtt_os_load_average_5m = Gauge(
    "ziggy_zigbee2mqtt_os_load_average_5m",
    "5-minute CPU load average",
    labelnames=["bridge_name"],
)

zigbee2mqtt_os_load_average_15m = Gauge(
    "ziggy_zigbee2mqtt_os_load_average_15m",
    "15-minute CPU load average",
    labelnames=["bridge_name"],
)

zigbee2mqtt_os_memory_used_mb = Gauge(
    "ziggy_zigbee2mqtt_os_memory_used_mb",
    "Amount of used memory in MB",
    labelnames=["bridge_name"],
)

zigbee2mqtt_os_memory_percent = Gauge(
    "ziggy_zigbee2mqtt_os_memory_percent",
    "Amount of used memory in percentage",
    labelnames=["bridge_name"],
)

# Process Metrics
zigbee2mqtt_process_uptime_seconds = Gauge(
    "ziggy_zigbee2mqtt_process_uptime_seconds",
    "Uptime of Zigbee2MQTT in seconds",
    labelnames=["bridge_name"],
)

zigbee2mqtt_process_memory_used_mb = Gauge(
    "ziggy_zigbee2mqtt_process_memory_used_mb",
    "Memory used by Zigbee2MQTT in MB",
    labelnames=["bridge_name"],
)

zigbee2mqtt_process_memory_percent = Gauge(
    "ziggy_zigbee2mqtt_process_memory_percent",
    "Memory used by Zigbee2MQTT in percentage",
    labelnames=["bridge_name"],
)

# MQTT Metrics
zigbee2mqtt_mqtt_connected = Gauge(
    "ziggy_zigbee2mqtt_mqtt_connected",
    "Whether Zigbee2MQTT is connected to MQTT",
    labelnames=["bridge_name"],
)

zigbee2mqtt_mqtt_queued_messages = Gauge(
    "ziggy_zigbee2mqtt_mqtt_queued_messages",
    "Amount of queued messages to be sent to MQTT",
    labelnames=["bridge_name"],
)

zigbee2mqtt_mqtt_published_messages = Counter(
    "ziggy_zigbee2mqtt_mqtt_published_messages_total",
    "Amount of published MQTT messages",
    labelnames=["bridge_name"],
)

zigbee2mqtt_mqtt_received_messages = Counter(
    "ziggy_zigbee2mqtt_mqtt_received_messages_total",
    "Amount of received MQTT messages",
    labelnames=["bridge_name"],
)

# Device Metrics
zigbee2mqtt_device_leave_count = Gauge(
    "ziggy_zigbee2mqtt_device_leave_count",
    "Current number of times the device left the network",
    labelnames=["bridge_name", "device_ieee"],
)

zigbee2mqtt_device_network_address_changes = Gauge(
    "ziggy_zigbee2mqtt_device_network_address_changes",
    "Current number of times the device changed its network address",
    labelnames=["bridge_name", "device_ieee"],
)

zigbee2mqtt_device_messages = Gauge(
    "ziggy_zigbee2mqtt_device_messages",
    "Current number of messages received from the device",
    labelnames=["bridge_name", "device_ieee"],
)

zigbee2mqtt_device_messages_per_sec = Gauge(
    "ziggy_zigbee2mqtt_device_messages_per_sec",
    "Current messages per second received from the device",
    labelnames=["bridge_name", "device_ieee"],
)

# Device Appearance Counter
zigbee2mqtt_device_appearances = Counter(
    "ziggy_zigbee2mqtt_device_appearances_total",
    "Total number of times a device appeared in health messages",
    labelnames=["bridge_name", "device_ieee"],
)

# Bridge Info
zigbee2mqtt_bridge_info = Info(
    "ziggy_zigbee2mqtt_bridge",
    "Zigbee2MQTT bridge information",
    labelnames=["bridge_name"],
)

# Base Topic Info
zigbee2mqtt_base_topic_info = Info(
    "ziggy_zigbee2mqtt_base_topic",
    "Zigbee2MQTT base topic information",
    labelnames=["bridge_name"],
)


class Zigbee2MQTTMetrics:
    """Class to manage Zigbee2MQTT health-related Prometheus metrics."""

    def __init__(
        self, bridge_name: str = "default", base_topic: str = "zigbee2mqtt"
    ):
        """Initialize Zigbee2MQTT metrics with bridge information."""
        self.bridge_name = bridge_name
        self.base_topic = base_topic
        self.labels = {"bridge_name": bridge_name}

    def update_bridge_health(self, health_data: Dict[str, Any]):
        """Update all bridge health metrics from Zigbee2MQTT health data."""
        # Update timestamp
        if "response_time" in health_data:
            timestamp = (
                health_data["response_time"] / 1000
            )  # Convert from milliseconds to seconds
            zigbee2mqtt_bridge_health_timestamp.labels(**self.labels).set(
                timestamp
            )

        # Update OS metrics
        if "os" in health_data:
            os_data = health_data["os"]
            if "load_average" in os_data and len(os_data["load_average"]) >= 3:
                load_avg = os_data["load_average"]
                zigbee2mqtt_os_load_average_1m.labels(**self.labels).set(
                    load_avg[0]
                )
                zigbee2mqtt_os_load_average_5m.labels(**self.labels).set(
                    load_avg[1]
                )
                zigbee2mqtt_os_load_average_15m.labels(**self.labels).set(
                    load_avg[2]
                )

            if "memory_used_mb" in os_data:
                zigbee2mqtt_os_memory_used_mb.labels(**self.labels).set(
                    os_data["memory_used_mb"]
                )

            if "memory_percent" in os_data:
                zigbee2mqtt_os_memory_percent.labels(**self.labels).set(
                    os_data["memory_percent"]
                )

        # Update process metrics
        if "process" in health_data:
            process_data = health_data["process"]
            if "uptime_sec" in process_data:
                zigbee2mqtt_process_uptime_seconds.labels(**self.labels).set(
                    process_data["uptime_sec"]
                )

            if "memory_used_mb" in process_data:
                zigbee2mqtt_process_memory_used_mb.labels(**self.labels).set(
                    process_data["memory_used_mb"]
                )

            if "memory_percent" in process_data:
                zigbee2mqtt_process_memory_percent.labels(**self.labels).set(
                    process_data["memory_percent"]
                )

        # Update MQTT metrics
        if "mqtt" in health_data:
            mqtt_data = health_data["mqtt"]
            if "connected" in mqtt_data:
                zigbee2mqtt_mqtt_connected.labels(**self.labels).set(
                    1 if mqtt_data["connected"] else 0
                )

            if "queued_messages" in mqtt_data:
                zigbee2mqtt_mqtt_queued_messages.labels(**self.labels).set(
                    mqtt_data["queued_messages"]
                )

            if "published_messages_total" in mqtt_data:
                # For counters, we need to track the difference
                current_published = mqtt_data["published_messages_total"]
                # Note: This is a simplified approach. In a real implementation,
                # you might want to track the previous value to calculate the difference
                zigbee2mqtt_mqtt_published_messages.labels(**self.labels).inc(
                    current_published
                )

            if "received_messages_total" in mqtt_data:
                current_received = mqtt_data["received_messages_total"]
                zigbee2mqtt_mqtt_received_messages.labels(**self.labels).inc(
                    current_received
                )

        # Update device metrics
        if "devices" in health_data:
            devices_data = health_data["devices"]

            # Check if devices_data is a dictionary of individual devices or summary data
            if isinstance(devices_data, dict):
                # If it's a dictionary, check if it contains individual device data or summary data
                if "total" in devices_data or "active" in devices_data:
                    # This is summary data, not individual device data
                    # Skip individual device processing for summary data
                    pass
                else:
                    # This is individual device data
                    for device_ieee, device_data in devices_data.items():
                        device_labels = {
                            **self.labels,
                            "device_ieee": device_ieee,
                        }

                        if "leave_count" in device_data:
                            zigbee2mqtt_device_leave_count.labels(
                                **device_labels
                            ).set(device_data["leave_count"])

                        if "network_address_changes" in device_data:
                            zigbee2mqtt_device_network_address_changes.labels(
                                **device_labels
                            ).set(device_data["network_address_changes"])

                        if "messages" in device_data:
                            zigbee2mqtt_device_messages.labels(
                                **device_labels
                            ).set(device_data["messages"])

                        if "messages_per_sec" in device_data:
                            zigbee2mqtt_device_messages_per_sec.labels(
                                **device_labels
                            ).set(device_data["messages_per_sec"])

                        # Update device appearances counter
                        zigbee2mqtt_device_appearances.labels(
                            **device_labels
                        ).inc()

    def set_bridge_info(self, info: Dict[str, Any]):
        """Set bridge information."""
        # Filter out label keys from info to avoid conflicts
        info_without_labels = {
            k: v for k, v in info.items() if k not in self.labels
        }
        zigbee2mqtt_bridge_info.labels(**self.labels).info(info_without_labels)

    def set_base_topic_info(self, info: Dict[str, Any]):
        """Set base topic information."""
        # Filter out label keys from info to avoid conflicts
        info_without_labels = {
            k: v for k, v in info.items() if k not in self.labels
        }
        zigbee2mqtt_base_topic_info.labels(**self.labels).info(
            info_without_labels
        )

    def reset_device_metrics(self, device_ieee: str):
        """Reset metrics for a specific device."""
        device_labels = {**self.labels, "device_ieee": device_ieee}
        zigbee2mqtt_device_messages_per_sec.labels(**device_labels).set(0)
        zigbee2mqtt_device_messages.labels(**device_labels).set(0)
        zigbee2mqtt_device_network_address_changes.labels(**device_labels).set(
            0
        )
        zigbee2mqtt_device_leave_count.labels(**device_labels).set(0)


# Global metrics instance (will be set by the MQTT client)
zigbee2mqtt_metrics: Optional[Zigbee2MQTTMetrics] = None


def get_zigbee2mqtt_metrics() -> Optional[Zigbee2MQTTMetrics]:
    """Get the global Zigbee2MQTT metrics instance."""
    return zigbee2mqtt_metrics


def set_zigbee2mqtt_metrics(metrics: Zigbee2MQTTMetrics):
    """Set the global Zigbee2MQTT metrics instance."""
    global zigbee2mqtt_metrics
    zigbee2mqtt_metrics = metrics
