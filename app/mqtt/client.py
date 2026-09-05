import json
import logging

import paho.mqtt.client as mqtt

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.schemas.gps import GPSIngestRequest
from app.services.gps_service import record_location

logger = logging.getLogger(__name__)


def process_mqtt_payload(topic: str, payload: bytes) -> None:
    segments = topic.split("/")
    if len(segments) != 3 or segments[0] != "vehicles" or segments[2] != "location":
        raise ValueError("Invalid MQTT topic")
    vehicle_id = int(segments[1])
    data = GPSIngestRequest.model_validate_json(payload)
    with SessionLocal() as session:
        record_location(session, vehicle_id, data)


def start_mqtt_client() -> mqtt.Client:
    settings = get_settings()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="tracking-api")

    def on_connect(client: mqtt.Client, _userdata, _flags, reason_code, _properties) -> None:
        if reason_code.is_failure:
            logger.error("MQTT connection failed: %s", reason_code)
            return
        client.subscribe("vehicles/+/location")
        logger.info("Subscribed to vehicle location updates")

    def on_message(_client: mqtt.Client, _userdata, message: mqtt.MQTTMessage) -> None:
        try:
            process_mqtt_payload(message.topic, message.payload)
        except (ValueError, json.JSONDecodeError) as exc:
            logger.warning("Rejected MQTT message on %s: %s", message.topic, exc)
        except Exception:
            logger.exception("Unable to store MQTT message on %s", message.topic)

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect_async(settings.mqtt_host, settings.mqtt_port, 60)
    client.loop_start()
    return client
