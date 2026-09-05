from datetime import UTC, datetime

from pydantic import BaseModel, Field, field_validator


class GPSIngestRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    speed: float = Field(ge=0, le=250)
    recorded_at: datetime | None = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("recorded_at")
    @classmethod
    def make_timestamp_aware(cls, value: datetime | None) -> datetime:
        timestamp = value or datetime.now(UTC)
        return timestamp if timestamp.tzinfo else timestamp.replace(tzinfo=UTC)
