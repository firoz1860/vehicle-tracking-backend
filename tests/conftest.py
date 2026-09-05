from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import create_app
from app.models import GPSLocation, Route, User, UserAssignment, Vehicle


@pytest.fixture()
def client_and_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(engine)
    session = factory()
    route_a = Route(code="ROUTE-A", name="Route A", origin="North Campus", destination="Central Station", route_points=[{"latitude": 28.7041, "longitude": 77.1025}])
    route_b = Route(code="ROUTE-B", name="Route B", origin="East Terminal", destination="West Market", route_points=[{"latitude": 28.6139, "longitude": 77.2090}])
    bus_a = Vehicle(vehicle_number="BUS-001", route=route_a, model="Electric Shuttle", status="moving", latest_latitude=28.7041, latest_longitude=77.1025, latest_speed=24, latest_at=datetime.now(UTC))
    bus_b = Vehicle(vehicle_number="BUS-002", route=route_b, model="City Bus", status="stopped", latest_latitude=28.6139, latest_longitude=77.2090, latest_speed=0, latest_at=datetime.now(UTC))
    rider_a = User(email="rider.a@example.com", full_name="Rider A", password_hash=hash_password("Password123"))
    rider_b = User(email="rider.b@example.com", full_name="Rider B", password_hash=hash_password("Password123"))
    session.add_all([route_a, route_b, bus_a, bus_b, rider_a, rider_b])
    session.flush()
    session.add_all([UserAssignment(user=rider_a, route=route_a, vehicle=bus_a), UserAssignment(user=rider_b, route=route_b, vehicle=bus_b)])
    session.add(GPSLocation(vehicle_id=bus_b.id, latitude=28.6139, longitude=77.2090, speed=0, recorded_at=datetime.now(UTC)))
    session.commit()
    app = create_app()
    app.dependency_overrides[get_db] = lambda: session
    with TestClient(app) as test_client:
        yield test_client, session
    session.close()
    Base.metadata.drop_all(engine)
