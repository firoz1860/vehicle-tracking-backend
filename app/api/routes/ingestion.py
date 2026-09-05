from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.schemas.gps import GPSIngestRequest
from app.schemas.tracking import LocationResponse
from app.services.gps_service import record_location

router = APIRouter(prefix="/ingest", tags=["ingestion"])


def require_ingest_key(x_api_key: str = Header(default="")) -> None:
    if x_api_key != get_settings().gps_ingest_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid ingestion key")


@router.post("/vehicles/{vehicle_id}/location", response_model=LocationResponse, dependencies=[Depends(require_ingest_key)])
def ingest_location(vehicle_id: int, payload: GPSIngestRequest, session: Session = Depends(get_db)) -> LocationResponse:
    try:
        location = record_location(session, vehicle_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return LocationResponse(
        latitude=location.latitude,
        longitude=location.longitude,
        speed=location.speed,
        recorded_at=location.recorded_at,
    )
