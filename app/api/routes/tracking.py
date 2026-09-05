
from fastapi import APIRouter, HTTPException, Query

from app.dependencies.auth import CurrentUser, DbSession
from app.schemas.tracking import (
    DashboardResponse,
    HistoryResponse,
    LocationResponse,
    RouteResponse,
    VehicleResponse,
)
from app.services.tracking_service import get_assignment, get_history

router = APIRouter(prefix="/me", tags=["tracking"])


def route_response(route) -> RouteResponse:
    return RouteResponse(
        id=route.id,
        code=route.code,
        name=route.name,
        origin=route.origin,
        destination=route.destination,
        route_points=route.route_points,
    )


def vehicle_response(vehicle) -> VehicleResponse:
    return VehicleResponse(
        id=vehicle.id,
        vehicle_number=vehicle.vehicle_number,
        model=vehicle.model,
        status=vehicle.status,
    )


def latest_response(vehicle) -> LocationResponse | None:
    if vehicle.latest_latitude is None or vehicle.latest_longitude is None or vehicle.latest_at is None:
        return None
    return LocationResponse(
        latitude=vehicle.latest_latitude,
        longitude=vehicle.latest_longitude,
        speed=vehicle.latest_speed or 0,
        recorded_at=vehicle.latest_at,
    )


def assigned_or_404(session: DbSession, user: CurrentUser):
    try:
        return get_assignment(session, user)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(user: CurrentUser, session: DbSession) -> DashboardResponse:
    assignment = assigned_or_404(session, user)
    return DashboardResponse(
        route=route_response(assignment.route),
        vehicle=vehicle_response(assignment.vehicle),
        latest_location=latest_response(assignment.vehicle),
    )


@router.get("/route", response_model=RouteResponse)
def assigned_route(user: CurrentUser, session: DbSession) -> RouteResponse:
    return route_response(assigned_or_404(session, user).route)


@router.get("/vehicle", response_model=VehicleResponse)
def assigned_vehicle(user: CurrentUser, session: DbSession) -> VehicleResponse:
    return vehicle_response(assigned_or_404(session, user).vehicle)


@router.get("/location", response_model=LocationResponse | None)
def current_location(user: CurrentUser, session: DbSession) -> LocationResponse | None:
    return latest_response(assigned_or_404(session, user).vehicle)


@router.get("/history", response_model=HistoryResponse)
def location_history(
    user: CurrentUser,
    session: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> HistoryResponse:
    assignment = assigned_or_404(session, user)
    items = get_history(session, assignment.vehicle_id, page, page_size)
    return HistoryResponse(
        items=[
            LocationResponse(
                latitude=item.latitude,
                longitude=item.longitude,
                speed=item.speed,
                recorded_at=item.recorded_at,
            )
            for item in items
        ],
        page=page,
        page_size=page_size,
    )
