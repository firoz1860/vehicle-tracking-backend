# Vehicle Tracking Backend

Production-style FastAPI backend for a GPS-based bus tracking system. It securely authenticates riders, enforces one route and vehicle assignment per user, stores incoming GPS updates in PostgreSQL, and serves current and historical tracking data to the Flutter application.

## Live Links

* API: https://vehicle-tracking-backend-ylqw.onrender.com
* Interactive API documentation: https://vehicle-tracking-backend-ylqw.onrender.com/docs
* Live Flutter application: https://eloquent-moxie-380c44.netlify.app
* Flutter repository: https://github.com/firoz1860/vehicle-tracking-flutter

## Features

* JWT-based authentication for multiple users
* PostgreSQL database hosted on Neon
* One backend-enforced route and vehicle assignment per user
* MQTT GPS ingestion support
* API-key-protected REST GPS ingestion fallback
* Current vehicle location and historical GPS records
* Protected route, vehicle, location, and history APIs
* Clean modular FastAPI architecture
* Docker Compose setup with PostgreSQL, MQTT broker, API, and GPS simulator
* Input validation, CORS configuration, health endpoint, and automated backend tests

## System Architecture

```text
GPS Device / Simulator
        |
        | MQTT or protected REST request
        v
FastAPI Backend on Render
        |
        v
Neon PostgreSQL Database
        |
        v
Flutter Tracking Application on Netlify
```

## GPS Data Flow

```text
Vehicle GPS update
  -> FastAPI validates the request
  -> GPS record is added to gps_locations
  -> latest latitude, longitude, speed, time, and status update in vehicles
  -> Flutter app loads the assigned vehicle dashboard
```

## Technology Stack

| Layer             | Technology                    |
| ----------------- | ----------------------------- |
| Backend           | Python, FastAPI               |
| Database          | PostgreSQL, SQLAlchemy        |
| Authentication    | JWT Bearer Token              |
| Password security | Salted scrypt password hashes |
| GPS ingestion     | MQTT and REST API             |
| Deployment        | Render                        |
| Database hosting  | Neon PostgreSQL               |
| API documentation | Swagger / OpenAPI             |

## Demo Accounts

| User    | Email                 | Password      | Assigned route | Assigned vehicle |
| ------- | --------------------- | ------------- | -------------- | ---------------- |
| Rider A | `rider.a@example.com` | `Password123` | Campus Express | BUS-001          |
| Rider B | `rider.b@example.com` | `Password123` | City Connector | BUS-002          |

## Authorization Logic

The backend, not the Flutter client, controls assignment access.

1. The user logs in and receives a JWT.
2. Every protected request reads the authenticated user from the JWT.
3. The backend finds that user's `user_assignments` record.
4. The backend returns only the route and vehicle assigned to that user.
5. The client never sends a route ID or vehicle ID when requesting dashboard data.

This prevents Rider A from viewing BUS-002 and prevents Rider B from viewing BUS-001.

## Database Design

| Table              | Purpose                                                           |
| ------------------ | ----------------------------------------------------------------- |
| `users`            | Rider accounts, email, password hash, active status               |
| `routes`           | Route code, route name, origin, destination, map coordinates      |
| `vehicles`         | Bus number, model, current status, latest GPS values              |
| `user_assignments` | One route and vehicle mapping for each user                       |
| `gps_locations`    | Historical latitude, longitude, speed, vehicle ID, and timestamps |

`gps_locations` is indexed by vehicle and recorded time for efficient tracking-history queries.

## API Endpoints

| Method | Endpoint                                        | Authentication | Purpose                                      |
| ------ | ----------------------------------------------- | -------------- | -------------------------------------------- |
| `POST` | `/api/v1/auth/login`                            | No             | Log in and receive JWT                       |
| `GET`  | `/api/v1/me/dashboard`                          | JWT            | Assigned route, vehicle, and latest location |
| `GET`  | `/api/v1/me/route`                              | JWT            | Assigned route                               |
| `GET`  | `/api/v1/me/vehicle`                            | JWT            | Assigned vehicle                             |
| `GET`  | `/api/v1/me/location`                           | JWT            | Latest GPS location                          |
| `GET`  | `/api/v1/me/history`                            | JWT            | Historical GPS locations                     |
| `POST` | `/api/v1/ingest/vehicles/{vehicle_id}/location` | API key        | Store a GPS update                           |
| `GET`  | `/health`                                       | No             | Health check                                 |

## Example GPS Ingestion Request

Use the Swagger documentation or send a protected request:

```bash
curl -X POST "https://vehicle-tracking-backend-ylqw.onrender.com/api/v1/ingest/vehicles/2/location" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_GPS_INGEST_API_KEY" \
  -d '{
    "latitude": 28.6500,
    "longitude": 77.2350,
    "speed": 22,
    "recorded_at": "2026-09-05T16:00:00Z"
  }'
```

A successful GPS update is stored in PostgreSQL and updates the assigned vehicle's latest location, speed, and moving/stopped status.

## Environment Variables

| Variable                      | Required | Description                                 |
| ----------------------------- | -------- | ------------------------------------------- |
| `TRACKING_DATABASE_URL`       | Yes      | Neon PostgreSQL connection string           |
| `TRACKING_JWT_SECRET`         | Yes      | Long private secret used to sign JWT tokens |
| `TRACKING_GPS_INGEST_API_KEY` | Yes      | Secret required by GPS REST ingestion       |
| `TRACKING_CORS_ORIGINS`       | Yes      | Allowed frontend URL                        |
| `TRACKING_MQTT_HOST`          | Optional | MQTT broker host                            |
| `TRACKING_MQTT_PORT`          | Optional | MQTT broker port                            |

Never commit actual secrets to GitHub.

## Run Locally with Docker

```bash
docker compose up --build
```

This starts:

* PostgreSQL database
* Mosquitto MQTT broker
* FastAPI backend
* GPS simulator publishing coordinates every eight seconds

Open Swagger documentation at:

```text
http://localhost:8000/docs
```

## Run Tests

```bash
pip install -e ".[dev]"
pytest -v
ruff check app tests
```

## Database Evidence

The following screenshots prove that PostgreSQL stores routes, vehicle assignments, latest vehicle state, and historical GPS data.

### GPS History Stored in `gps_locations`

<!-- In GitHub edit mode, drag the gps_locations screenshot here. -->

### Route Records Stored in `routes`

<!-- In GitHub edit mode, drag the routes screenshot here. -->

### Backend-Enforced Mapping in `user_assignments`

<!-- In GitHub edit mode, drag the user_assignments screenshot here. -->

### Latest Vehicle State in `vehicles`

<!-- In GitHub edit mode, drag the vehicles screenshot here. -->

## Assessment Coverage

* Multiple authenticated users: complete
* PostgreSQL data storage: complete
* One route and vehicle per user: complete
* Backend authorization: complete
* MQTT and REST GPS ingestion: complete
* Latest and historical GPS records: complete
* Flutter API support: complete
* Docker Compose and GPS simulator bonus: complete
