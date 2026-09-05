from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import GPSLocation, User, UserAssignment


def get_assignment(session: Session, user: User) -> UserAssignment:
    assignment = session.scalar(
        select(UserAssignment)
        .options(joinedload(UserAssignment.route), joinedload(UserAssignment.vehicle))
        .where(UserAssignment.user_id == user.id)
    )
    if not assignment or assignment.vehicle.route_id != assignment.route_id:
        raise LookupError("No valid vehicle assignment found")
    return assignment


def get_history(session: Session, vehicle_id: int, page: int, page_size: int) -> list[GPSLocation]:
    return list(
        session.scalars(
            select(GPSLocation)
            .where(GPSLocation.vehicle_id == vehicle_id)
            .order_by(GPSLocation.recorded_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    )
