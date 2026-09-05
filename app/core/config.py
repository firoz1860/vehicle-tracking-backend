from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Vehicle Tracking API"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://tracking:tracking@db:5432/tracking"
    jwt_secret: str = "replace-this-development-secret-with-at-least-32-characters"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60
    gps_ingest_api_key: str = "replace-this-ingest-key"
    mqtt_host: str = "mqtt"
    mqtt_port: int = 1883
    cors_origins: str = "*"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="TRACKING_", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
