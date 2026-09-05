from datetime import UTC, datetime

from sqlalchemy import select

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import GPSLocation, Route, User, UserAssignment, Vehicle

ROUTE_A_POINTS = [
    {"latitude": 28.7041, "longitude": 77.1025},
    {"latitude": 28.6972, "longitude": 77.1201},
    {"latitude": 28.6863, "longitude": 77.1410},
]
ROUTE_B_POINTS = [
    {"latitude": 28.6139, "longitude": 77.2090},
    {"latitude": 28.6250, "longitude": 77.2250},
    {"latitude": 28.6400, "longitude": 77.2400},
]


def seed_demo_data() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        if session.scalar(select(User.id).limit(1)):
            return
        route_a = Route(code="ROUTE-A", name="Campus Express", origin="North Campus", destination="Central Station", route_points=ROUTE_A_POINTS)
        route_b = Route(code="ROUTE-B", name="City Connector", origin="East Terminal", destination="West Market", route_points=ROUTE_B_POINTS)
        bus_a = Vehicle(vehicle_number="BUS-001", route=route_a, model="Electric Shuttle", status="moving", latest_latitude=28.7041, latest_longitude=77.1025, latest_speed=20, latest_at=datetime.now(UTC))
        bus_b = Vehicle(vehicle_number="BUS-002", route=route_b, model="City Bus", status="stopped", latest_latitude=28.6139, latest_longitude=77.2090, latest_speed=0, latest_at=datetime.now(UTC))
        rider_a = User(email="rider.a@example.com", full_name="Rider A", password_hash=hash_password("Password123"))
        rider_b = User(email="rider.b@example.com", full_name="Rider B", password_hash=hash_password("Password123"))
        session.add_all([route_a, route_b, bus_a, bus_b, rider_a, rider_b])
        session.flush()
        session.add_all([
            UserAssignment(user=rider_a, route=route_a, vehicle=bus_a),
            UserAssignment(user=rider_b, route=route_b, vehicle=bus_b),
            GPSLocation(vehicle_id=bus_a.id, latitude=28.7041, longitude=77.1025, speed=20, recorded_at=datetime.now(UTC)),
            GPSLocation(vehicle_id=bus_b.id, latitude=28.6139, longitude=77.2090, speed=0, recorded_at=datetime.now(UTC)),
        ])
        session.commit()


if __name__ == "__main__":
    seed_demo_data()
    print("Demo users, routes, vehicles, assignments, and GPS positions are ready.")
