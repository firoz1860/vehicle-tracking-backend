from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.models import Vehicle
from app.schemas.gps import GPSIngestRequest
from app.services.gps_service import record_location


def test_record_location_updates_current_vehicle_state(client_and_session):
    _, session = client_and_session
    vehicle = session.query(Vehicle).filter_by(vehicle_number="BUS-001").one()
    position = record_location(session, vehicle.id, GPSIngestRequest(latitude=28.71, longitude=77.11, speed=32, recorded_at=datetime.now(UTC)))

    session.refresh(vehicle)
    assert position.vehicle_id == vehicle.id
    assert vehicle.latest_latitude == 28.71
    assert vehicle.status == "moving"


def test_gps_payload_rejects_invalid_coordinates():
    with pytest.raises(ValidationError):
        GPSIngestRequest(latitude=91, longitude=77.11, speed=20)
