#!/usr/bin/env python3
"""
Test script to subscribe to the MQTT topic and verify message reception.
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


def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker."""
    if rc == 0:
        print(
            f"✅ Connected to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}"
        )
        # Subscribe to the topic
        print(f"📡 Subscribing to topic: {TOPIC}")
        client.subscribe(TOPIC)
    else:
        print(f"❌ Failed to connect to MQTT broker, return code: {rc}")


def on_message(client, userdata, msg):
    """Callback when message is received."""
    print("🎯 MESSAGE RECEIVED!")
    print(f"   Topic: {msg.topic}")
    print(f"   Payload: {msg.payload.decode()}")
    print(f"   QoS: {msg.qos}")

    try:
        data = json.loads(msg.payload.decode())
        print(f"   Parsed JSON: {json.dumps(data, indent=2)}")
    except json.JSONDecodeError:
        print(f"   Raw payload: {msg.payload}")


def on_subscribe(client, userdata, mid, granted_qos):
    """Callback when subscription is successful."""
    print(f"✅ Successfully subscribed to topic (message ID: {mid})")


def main():
    """Main function to subscribe and listen for messages."""
    print(f"🎧 Starting MQTT subscription test for topic: {TOPIC}")
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
    client.on_message = on_message
    client.on_subscribe = on_subscribe

    try:
        # Connect to broker
        print(
            f"🔌 Connecting to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}..."
        )
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)

        # Start the loop
        client.loop_start()

        print("⏳ Listening for messages... (Press Ctrl+C to stop)")

        # Keep running for 30 seconds
        time.sleep(30)

        # Stop the loop
        client.loop_stop()
        client.disconnect()

        print("✅ Test completed!")

    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        client.loop_stop()
        client.disconnect()
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
