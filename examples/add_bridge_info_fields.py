#!/usr/bin/env python3
"""
Example script showing how to add or remove fields from bridge info metrics.

This demonstrates how to customize which fields are included in the bridge info
Prometheus metrics.
"""

import os
import sys


def setup_path():
    """Add the project root to the Python path."""
    project_root = os.path.join(os.path.dirname(__file__), "..")
    sys.path.insert(0, project_root)


def main():
    """Demonstrate how to customize bridge info metrics."""
    # Setup path before importing app modules
    setup_path()

    from app.zigbee2mqtt_metrics import (
        BRIDGE_INFO_INCLUDED_FIELDS,
        add_bridge_info_field,
        remove_bridge_info_field,
    )

    print("Current bridge info fields configuration:")
    for category, fields in BRIDGE_INFO_INCLUDED_FIELDS.items():
        print(f"  {category}: {fields}")

    print("\n" + "=" * 50)
    print("Adding fields to bridge info metrics...")

    # Add a field to version metrics
    add_bridge_info_field("version", "build_date")
    print("✓ Added 'build_date' to version metrics")

    # Add a field to coordinator metrics
    add_bridge_info_field("coordinator", "meta_majorrel")
    print("✓ Added 'meta_majorrel' to coordinator metrics")

    # Add a field to config metrics
    add_bridge_info_field("config", "mqtt_client_id")
    print("✓ Added 'mqtt_client_id' to config metrics")

    print("\nUpdated configuration:")
    for category, fields in BRIDGE_INFO_INCLUDED_FIELDS.items():
        print(f"  {category}: {fields}")

    print("\n" + "=" * 50)
    print("Removing fields from bridge info metrics...")

    # Remove a field from config metrics
    remove_bridge_info_field("config", "mqtt_client_id")
    print("✓ Removed 'mqtt_client_id' from config metrics")

    print("\nFinal configuration:")
    for category, fields in BRIDGE_INFO_INCLUDED_FIELDS.items():
        print(f"  {category}: {fields}")


if __name__ == "__main__":
    main()
