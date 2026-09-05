
from sqlalchemy.orm import Session

from app.models import GPSLocation, Vehicle
from app.schemas.gps import GPSIngestRequest


def record_location(session: Session, vehicle_id: int, data: GPSIngestRequest) -> GPSLocation:
    vehicle = session.get(Vehicle, vehicle_id)
    if not vehicle:
        raise LookupError("Vehicle not found")
    location = GPSLocation(
        vehicle_id=vehicle.id,
        latitude=data.latitude,
        longitude=data.longitude,
        speed=data.speed,
        recorded_at=data.recorded_at,
    )
    vehicle.latest_latitude = data.latitude
    vehicle.latest_longitude = data.longitude
    vehicle.latest_speed = data.speed
    vehicle.latest_at = data.recorded_at
    vehicle.status = "moving" if data.speed > 1 else "stopped"
    session.add(location)
    session.commit()
    session.refresh(location)
    return location
