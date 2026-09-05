from datetime import datetime

from pydantic import BaseModel


class RoutePoint(BaseModel):
    latitude: float
    longitude: float


class RouteResponse(BaseModel):
    id: int
    code: str
    name: str
    origin: str
    destination: str
    route_points: list[RoutePoint]


class VehicleResponse(BaseModel):
    id: int
    vehicle_number: str
    model: str
    status: str


class LocationResponse(BaseModel):
    latitude: float
    longitude: float
    speed: float
    recorded_at: datetime


class DashboardResponse(BaseModel):
    route: RouteResponse
    vehicle: VehicleResponse
    latest_location: LocationResponse | None


class HistoryResponse(BaseModel):
    items: list[LocationResponse]
    page: int
    page_size: int
