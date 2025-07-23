from app.zigbee2mqtt_metrics import (
    BRIDGE_INFO_INCLUDED_FIELDS,
    Zigbee2MQTTMetrics,
)


class TestBridgeInfoFix:
    """Test cases for the fixed bridge info structure."""

    def test_bridge_info_structure_matches_actual_json(self):
        """Test that the bridge info structure matches the actual Zigbee2MQTT JSON."""
        # Sample data matching the actual Zigbee2MQTT bridge info structure
        sample_bridge_info = {
            "version": "1.13.0-dev",
            "commit": "772f6c0",
            "coordinator": {
                "ieee_address": "0x12345678",
                "type": "zStack30x",
                "meta": {
                    "revision": 20190425,
                    "transportrev": 2,
                    "product": 2,
                    "majorrel": 2,
                    "minorrel": 7,
                    "maintrel": 2,
                },
            },
            "zigbee_herdsman_converters": {"version": "15.98.0"},
            "zigbee_herdsman": {"version": "0.20.0"},
            "network": {
                "channel": 15,
                "pan_id": 5674,
                "extended_pan_id": [0, 11, 22],
            },
            "log_level": "debug",
            "permit_join": True,
            "permit_join_end": 1733666394,
            "config": {"some_config": "value"},
            "config_schema": {"some_schema": "value"},
            "restart_required": False,
            "os": {
                "version": "Linux - 0.0.1 - x64",
                "node_version": "v1.2.3",
                "cpus": "Intel Core i7-9999 (x1)",
                "memory_mb": 10,
            },
            "mqtt": {"server": "mqtt://localhost:1883", "version": 5},
        }

        # Create metrics instance
        metrics = Zigbee2MQTTMetrics(bridge_name="test-bridge")

        # Update bridge info
        metrics.update_bridge_info(sample_bridge_info)

        # Verify that the configuration includes the correct categories
        expected_categories = [
            "version",
            "coordinator",
            "network",
            "bridge",
            "os",
            "mqtt",
        ]
        assert list(BRIDGE_INFO_INCLUDED_FIELDS.keys()) == expected_categories

        # Verify that the fields are correctly mapped
        assert BRIDGE_INFO_INCLUDED_FIELDS["version"] == ["version", "commit"]
        assert BRIDGE_INFO_INCLUDED_FIELDS["coordinator"] == [
            "ieee_address",
            "type",
        ]
        assert BRIDGE_INFO_INCLUDED_FIELDS["network"] == [
            "channel",
            "pan_id",
            "extended_pan_id",
        ]
        assert BRIDGE_INFO_INCLUDED_FIELDS["bridge"] == [
            "log_level",
            "permit_join",
            "permit_join_end",
            "restart_required",
        ]
        assert BRIDGE_INFO_INCLUDED_FIELDS["os"] == [
            "version",
            "node_version",
            "cpus",
            "memory_mb",
        ]
        assert BRIDGE_INFO_INCLUDED_FIELDS["mqtt"] == ["server", "version"]

    def test_bridge_info_handles_missing_fields_gracefully(self):
        """Test that bridge info handles missing fields gracefully."""
        # Sample data with missing fields
        incomplete_bridge_info = {
            "version": "1.13.0-dev",
            "coordinator": {
                "ieee_address": "0x12345678"
                # Missing "type" field
            },
            "network": {
                "channel": 15
                # Missing "pan_id" and "extended_pan_id" fields
            },
            "log_level": "debug",
            # Missing other bridge fields
        }

        # Create metrics instance
        metrics = Zigbee2MQTTMetrics(bridge_name="test-bridge")

        # This should not raise an exception
        metrics.update_bridge_info(incomplete_bridge_info)

    def test_bridge_info_handles_nested_objects_correctly(self):
        """Test that bridge info handles nested objects correctly."""
        # Sample data with nested objects
        nested_bridge_info = {
            "version": "1.13.0-dev",
            "commit": "772f6c0",
            "coordinator": {
                "ieee_address": "0x12345678",
                "type": "zStack30x",
                "meta": {"revision": 20190425, "transportrev": 2},
            },
            "network": {
                "channel": 15,
                "pan_id": 5674,
                "extended_pan_id": [0, 11, 22],
            },
            "os": {
                "version": "Linux - 0.0.1 - x64",
                "node_version": "v1.2.3",
                "cpus": "Intel Core i7-9999 (x1)",
                "memory_mb": 10,
            },
            "mqtt": {"server": "mqtt://localhost:1883", "version": 5},
        }

        # Create metrics instance
        metrics = Zigbee2MQTTMetrics(bridge_name="test-bridge")

        # This should not raise an exception and should handle nested objects
        metrics.update_bridge_info(nested_bridge_info)

    def test_bridge_info_field_management_functions(self):
        """Test that the field management functions work with new categories."""
        from app.zigbee2mqtt_metrics import (
            add_bridge_info_field,
            remove_bridge_info_field,
        )

        # Test adding a field to a new category
        add_bridge_info_field("network", "new_field")
        assert "new_field" in BRIDGE_INFO_INCLUDED_FIELDS["network"]

        # Test removing a field
        remove_bridge_info_field("network", "new_field")
        assert "new_field" not in BRIDGE_INFO_INCLUDED_FIELDS["network"]

        # Test adding to bridge category (root level fields)
        add_bridge_info_field("bridge", "new_bridge_field")
        assert "new_bridge_field" in BRIDGE_INFO_INCLUDED_FIELDS["bridge"]

        # Clean up
        remove_bridge_info_field("bridge", "new_bridge_field")
