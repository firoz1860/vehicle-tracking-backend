from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    assignment: Mapped["UserAssignment | None"] = relationship(back_populates="user", uselist=False)


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    origin: Mapped[str] = mapped_column(String(120))
    destination: Mapped[str] = mapped_column(String(120))
    route_points: Mapped[list[dict]] = mapped_column(JSON, default=list)
    vehicles: Mapped[list["Vehicle"]] = relationship(back_populates="route")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_number: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id", ondelete="RESTRICT"))
    model: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(30), default="offline")
    latest_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    latest_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    latest_speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    latest_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    route: Mapped[Route] = relationship(back_populates="vehicles")
    locations: Mapped[list["GPSLocation"]] = relationship(back_populates="vehicle", cascade="all, delete-orphan")


class UserAssignment(Base):
    __tablename__ = "user_assignments"
    __table_args__ = (UniqueConstraint("user_id", name="uq_assignment_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id", ondelete="RESTRICT"))
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id", ondelete="RESTRICT"))
    user: Mapped[User] = relationship(back_populates="assignment")
    route: Mapped[Route] = relationship()
    vehicle: Mapped[Vehicle] = relationship()


class GPSLocation(Base):
    __tablename__ = "gps_locations"
    __table_args__ = (Index("ix_gps_vehicle_recorded_at", "vehicle_id", "recorded_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id", ondelete="CASCADE"))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    speed: Mapped[float] = mapped_column(Float, default=0)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    vehicle: Mapped[Vehicle] = relationship(back_populates="locations")
