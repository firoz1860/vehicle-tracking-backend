import json
import os
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

BROKER = os.getenv("MQTT_HOST", "mqtt")
POSITIONS = {
    1: [(28.7041, 77.1025), (28.6972, 77.1201), (28.6863, 77.1410)],
    2: [(28.6139, 77.2090), (28.6250, 77.2250), (28.6400, 77.2400)],
}

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="gps-simulator")
while True:
    try:
        client.connect(BROKER, 1883, 60)
        break
    except OSError:
        time.sleep(2)

index = 0
while True:
    for vehicle_id, points in POSITIONS.items():
        latitude, longitude = points[index % len(points)]
        client.publish(
            f"vehicles/{vehicle_id}/location",
            json.dumps({"latitude": latitude, "longitude": longitude, "speed": 24 if vehicle_id == 1 else 18, "recorded_at": datetime.now(timezone.utc).isoformat()}),
        )
    index += 1
    time.sleep(8)
