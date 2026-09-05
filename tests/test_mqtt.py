import pytest

from app.mqtt.client import process_mqtt_payload


def test_mqtt_payload_rejects_an_invalid_topic():
    with pytest.raises(ValueError, match="Invalid MQTT topic"):
        process_mqtt_payload("untrusted/topic", b'{"latitude":28.7,"longitude":77.1,"speed":10}')
