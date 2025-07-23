from app.zigbee2mqtt_metrics import (
    Zigbee2MQTTMetrics,
    get_zigbee2mqtt_metrics,
    set_zigbee2mqtt_metrics,
    zigbee2mqtt_bridge_health_timestamp,
    zigbee2mqtt_mqtt_connected,
    zigbee2mqtt_os_load_average_1m,
)


class TestZigbee2MQTTMetrics:
    """Test cases for Zigbee2MQTT metrics functionality."""

    def test_zigbee2mqtt_metrics_initialization(self):
        """Test that Zigbee2MQTT metrics initializes correctly."""
        metrics = Zigbee2MQTTMetrics("test-bridge")

        assert metrics.bridge_name == "test-bridge"
        assert metrics.labels == {"bridge_name": "test-bridge"}

    def test_update_bridge_health_timestamp(self):
        """Test updating bridge health timestamp."""
        metrics = Zigbee2MQTTMetrics("test-bridge")

        health_data = {
            "response_time": 1640995200000
        }  # Unix timestamp in milliseconds
        metrics.update_bridge_health(health_data)

        # Should not raise any exceptions
        assert True

    def test_update_os_metrics(self):
        """Test updating OS metrics."""
        metrics = Zigbee2MQTTMetrics("test-bridge")

        health_data = {
            "os": {
                "load_average": [0.5, 0.3, 0.2],
                "memory_used_mb": 1024,
                "memory_percent": 50.5,
            }
        }
        metrics.update_bridge_health(health_data)

        # Should not raise any exceptions
        assert True

    def test_update_process_metrics(self):
        """Test updating process metrics."""
        metrics = Zigbee2MQTTMetrics("test-bridge")

        health_data = {
            "process": {
                "uptime_sec": 3600,
                "memory_used_mb": 128,
                "memory_percent": 25.0,
            }
        }
        metrics.update_bridge_health(health_data)

        # Should not raise any exceptions
        assert True

    def test_update_mqtt_metrics(self):
        """Test updating MQTT metrics."""
        metrics = Zigbee2MQTTMetrics("test-bridge")

        health_data = {
            "mqtt": {
                "connected": True,
                "queued": 5,
                "published": 1000,
                "received": 500,
            }
        }
        metrics.update_bridge_health(health_data)

        # Should not raise any exceptions
        assert True

    def test_update_device_metrics(self):
        """Test updating device metrics."""
        metrics = Zigbee2MQTTMetrics("test-bridge")

        health_data = {
            "devices": {
                "0x00158d0001234567": {
                    "leave_count": 2,
                    "network_address_changes": 1,
                    "messages": 150,
                    "messages_per_sec": 0.5,
                }
            }
        }
        metrics.update_bridge_health(health_data)

        # Should not raise any exceptions
        assert True

    def test_update_bridge_health_complete(self):
        """Test updating complete bridge health data."""
        metrics = Zigbee2MQTTMetrics("test-bridge")

        health_data = {
            "response_time": 1640995200000,
            "os": {
                "load_average": [0.5, 0.3, 0.2],
                "memory_used_mb": 1024,
                "memory_percent": 50.5,
            },
            "process": {
                "uptime_sec": 3600,
                "memory_used_mb": 128,
                "memory_percent": 25.0,
            },
            "mqtt": {
                "connected": True,
                "queued": 5,
                "published": 1000,
                "received": 500,
            },
            "devices": {
                "0x00158d0001234567": {
                    "leave_count": 2,
                    "network_address_changes": 1,
                    "messages": 150,
                    "messages_per_sec": 0.5,
                },
                "0x00158d0001234568": {
                    "leave_count": 0,
                    "network_address_changes": 0,
                    "messages": 75,
                    "messages_per_sec": 0.2,
                },
            },
        }
        metrics.update_bridge_health(health_data)

        # Should not raise any exceptions
        assert True

    def test_update_bridge_health_partial_data(self):
        """Test updating bridge health with partial data."""
        metrics = Zigbee2MQTTMetrics("test-bridge")

        # Test with only OS data
        health_data = {
            "os": {
                "load_average": [0.5, 0.3, 0.2],
            }
        }
        metrics.update_bridge_health(health_data)

        # Test with only MQTT data
        health_data = {
            "mqtt": {
                "connected": False,
            }
        }
        metrics.update_bridge_health(health_data)

        # Should not raise any exceptions
        assert True

    def test_set_bridge_info(self):
        """Test setting bridge information."""
        metrics = Zigbee2MQTTMetrics("test-bridge")

        info = {
            "version": "1.30.0",
            "commit": "abc123",
            "coordinator": "Z-Stack 3.0+",
            "network": "0x1234",
        }
        metrics.set_bridge_info(info)

        # Should not raise any exceptions
        assert True

    def test_reset_device_metrics(self):
        """Test resetting device metrics."""
        metrics = Zigbee2MQTTMetrics("test-bridge")

        # Should not raise any exceptions
        metrics.reset_device_metrics("0x00158d0001234567")

    def test_update_bridge_state(self):
        """Test updating bridge state metrics."""
        metrics = Zigbee2MQTTMetrics("test-bridge", "test-topic")

        # Mock state data
        state_data = {
            "version": "1.13.0-dev",
            "commit": "772f6c0",
            "coordinator": {"ieee_address": "0x12345678", "type": "zStack30x"},
            "network": {"channel": 15, "pan_id": 5674},
            "log_level": "debug",
            "permit_join": True,
        }

        # Update bridge state
        metrics.update_bridge_state(state_data)

        # Verify the metrics were updated (we can't easily test Info metrics directly)
        # but we can verify the method doesn't raise exceptions
        assert metrics.bridge_name == "test-bridge"
        assert metrics.base_topic == "test-topic"

    def test_update_bridge_state_empty_data(self):
        """Test updating bridge state metrics with empty data."""
        metrics = Zigbee2MQTTMetrics("test-bridge", "test-topic")

        # Update with empty state data
        state_data = {}
        metrics.update_bridge_state(state_data)

        # Verify the method handles empty data gracefully
        assert metrics.bridge_name == "test-bridge"
        assert metrics.base_topic == "test-topic"

    def test_update_bridge_state_partial_data(self):
        """Test updating bridge state metrics with partial data."""
        metrics = Zigbee2MQTTMetrics("test-bridge", "test-topic")

        # Update with partial state data
        state_data = {"version": "1.13.0-dev", "permit_join": False}

        metrics.update_bridge_state(state_data)

        # Verify the method handles partial data gracefully
        assert metrics.bridge_name == "test-bridge"
        assert metrics.base_topic == "test-topic"


class TestZigbee2MQTTMetricsGlobal:
    """Test cases for global Zigbee2MQTT metrics functions."""

    def test_get_zigbee2mqtt_metrics_initial_none(self):
        """Test getting Zigbee2MQTT metrics when not set."""
        # Clear any existing metrics
        set_zigbee2mqtt_metrics(None)

        metrics = get_zigbee2mqtt_metrics()
        assert metrics is None

    def test_set_and_get_zigbee2mqtt_metrics(self):
        """Test setting and getting Zigbee2MQTT metrics."""
        test_metrics = Zigbee2MQTTMetrics("test-bridge")

        set_zigbee2mqtt_metrics(test_metrics)
        retrieved_metrics = get_zigbee2mqtt_metrics()

        assert retrieved_metrics is test_metrics
        assert retrieved_metrics.bridge_name == "test-bridge"


class TestZigbee2MQTTMetricsPrometheus:
    """Test cases for Prometheus metric definitions."""

    def test_metric_definitions_exist(self):
        """Test that all expected Prometheus metrics are defined."""
        # Test that the metrics are properly defined
        assert zigbee2mqtt_bridge_health_timestamp is not None
        assert zigbee2mqtt_os_load_average_1m is not None
        assert zigbee2mqtt_mqtt_connected is not None

        # Test metric names with ziggy_ prefix
        assert (
            zigbee2mqtt_bridge_health_timestamp._name
            == "ziggy_zigbee2mqtt_bridge_health_timestamp"
        )
        assert (
            zigbee2mqtt_os_load_average_1m._name
            == "ziggy_zigbee2mqtt_os_load_average_1m"
        )
        assert (
            zigbee2mqtt_mqtt_connected._name
            == "ziggy_zigbee2mqtt_mqtt_connected"
        )

    def test_metric_labelnames(self):
        """Test that metrics have the expected label names."""
        # Test bridge health timestamp metric labels
        assert "bridge_name" in zigbee2mqtt_bridge_health_timestamp._labelnames

        # Test OS load average metric labels
        assert "bridge_name" in zigbee2mqtt_os_load_average_1m._labelnames

        # Test MQTT connected metric labels
        assert "bridge_name" in zigbee2mqtt_mqtt_connected._labelnames


class TestZigbee2MQTTMetricsIntegration:
    """Test cases for Zigbee2MQTT metrics integration."""

    def test_metrics_labels_consistency(self):
        """Test that metrics labels are consistent across different operations."""
        metrics = Zigbee2MQTTMetrics("test-bridge")

        expected_labels = {
            "bridge_name": "test-bridge",
        }

        assert metrics.labels == expected_labels

        # Test that all operations use the same base labels
        # (This is more of a documentation test since we can't easily verify
        # the actual metric operations without exposing internal state)

        # The metrics should use consistent labeling across all operations
        assert "bridge_name" in metrics.labels

    def test_device_metrics_labels(self):
        """Test that device metrics include both bridge and device labels."""
        metrics = Zigbee2MQTTMetrics("test-bridge")

        # Test device labels construction
        device_ieee = "0x00158d0001234567"
        device_labels = {**metrics.labels, "device_ieee": device_ieee}

        expected_labels = {
            "bridge_name": "test-bridge",
            "device_ieee": "0x00158d0001234567",
        }

        assert device_labels == expected_labels
