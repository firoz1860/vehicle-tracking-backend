# Vehicle Tracking Backend

FastAPI service for an authenticated bus-tracking application. It consumes GPS events through MQTT, stores historical locations in PostgreSQL, and exposes only the route and vehicle assigned to the authenticated user.

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

The API is available at `http://localhost:8000`, with interactive OpenAPI docs at `/docs`. The first API container start creates the schema and demo data. The simulator publishes fresh positions every eight seconds.

### Demo accounts

| Email | Password | Assigned route | Assigned vehicle |
| --- | --- | --- | --- |
| `rider.a@example.com` | `Password123` | Campus Express / ROUTE-A | BUS-001 |
| `rider.b@example.com` | `Password123` | City Connector / ROUTE-B | BUS-002 |

## Architecture and GPS flow

`GPS simulator -> MQTT vehicles/{vehicle_id}/location -> FastAPI MQTT subscriber -> gps_locations + vehicle latest state -> protected FastAPI APIs -> Flutter`

`POST /api/v1/ingest/vehicles/{vehicle_id}/location` is an API-key-protected REST fallback for devices/integrations that cannot publish MQTT.

## Database design

- `users`: email, salted scrypt password hash, active status
- `routes`: code, name, endpoints and ordered map coordinates
- `vehicles`: route relationship plus denormalized latest location/status
- `user_assignments`: one unique assignment per user, linking that user to one route and vehicle
- `gps_locations`: append-only timestamped latitude, longitude, speed, vehicle records

The GPS table is indexed on `(vehicle_id, recorded_at)`. User assignments use foreign-key restrictions for route/vehicle integrity and cascade deletion only from user to assignment.

## Authentication and authorization

Login returns an expiring JWT. Protected endpoints resolve the user from the token, then resolve only that user's assignment. No endpoint accepts a vehicle ID or route ID from the mobile client for viewing data. The assignment service also verifies the assigned vehicle belongs to the assigned route; a manipulated client can never switch BUS-001 to BUS-002.

## API endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/api/v1/auth/login` | Login and return JWT |
| GET | `/api/v1/me/dashboard` | Assigned route, vehicle and current location |
| GET | `/api/v1/me/route` | Assigned route |
| GET | `/api/v1/me/vehicle` | Assigned vehicle |
| GET | `/api/v1/me/location` | Current vehicle location |
| GET | `/api/v1/me/history?page=1&page_size=20` | Assigned vehicle's location history |
| POST | `/api/v1/ingest/vehicles/{vehicle_id}/location` | API-key-protected GPS fallback |
| GET | `/health` | Liveness endpoint |

For local REST ingestion send `X-API-Key: local-ingest-key` and a JSON payload such as `{"latitude":28.71,"longitude":77.11,"speed":24,"recorded_at":"2026-09-05T10:00:00Z"}`.

## Local development and tests

```bash
python -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/pytest -v
.venv/bin/ruff check app tests
```

For production, replace all development secrets, turn off anonymous MQTT, use TLS/database backups, and run Alembic migrations instead of `create_all`.
