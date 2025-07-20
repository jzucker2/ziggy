#!/usr/bin/env python3
"""
Test script to publish a Zigbee2MQTT health message to the MQTT broker.
"""

import json
import os
import time

import paho.mqtt.client as mqtt

# MQTT Configuration from environment variables
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
TOPIC = os.getenv("ZIGBEE2MQTT_HEALTH_TOPIC", "zigbee2mqtt/bridge/health")

# Sample Zigbee2MQTT health data
health_data = {
    "response_time": int(
        time.time() * 1000
    ),  # Current timestamp in milliseconds
    "os": {
        "load_average": [0.5, 0.3, 0.2],
        "memory_used_mb": 512,
        "memory_percent": 25.5,
    },
    "process": {
        "uptime_seconds": 3600,
        "memory_used_mb": 128,
        "memory_percent": 12.5,
    },
    "mqtt": {
        "connected": True,
        "queued_messages": 0,
        "published_messages_total": 1500,
        "received_messages_total": 3000,
    },
    "devices": {
        "total": 15,
        "active": 12,
        "leave_count_total": 3,
        "network_address_changes_total": 2,
    },
}


def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker."""
    if rc == 0:
        print(
            f"✅ Connected to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}"
        )
    else:
        print(f"❌ Failed to connect to MQTT broker, return code: {rc}")


def on_publish(client, userdata, mid):
    """Callback when message is published."""
    print(f"✅ Message published successfully (message ID: {mid})")


def main():
    """Main function to publish test message."""
    print(f"🚀 Publishing test Zigbee2MQTT health message to topic: {TOPIC}")
    print(f"📊 Health data: {json.dumps(health_data, indent=2)}")
    print("🔌 MQTT Configuration:")
    print(f"   Host: {MQTT_BROKER_HOST}")
    print(f"   Port: {MQTT_BROKER_PORT}")
    print(f"   Username: {MQTT_USERNAME or 'None'}")
    print(f"   Password: {'***' if MQTT_PASSWORD else 'None'}")

    # Create MQTT client
    client = mqtt.Client()
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_publish = on_publish

    try:
        # Connect to broker
        print(
            f"🔌 Connecting to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}..."
        )
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)

        # Start the loop
        client.loop_start()

        # Wait a moment for connection
        time.sleep(2)

        # Publish the message
        message = json.dumps(health_data)
        print(f"📤 Publishing message to topic: {TOPIC}")
        client.publish(TOPIC, message, qos=0)

        # Wait for publish callback
        time.sleep(2)

        # Stop the loop
        client.loop_stop()
        client.disconnect()

        print("✅ Test completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
