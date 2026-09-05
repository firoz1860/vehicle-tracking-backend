def login(client, email):
    return client.post("/api/v1/auth/login", json={"email": email, "password": "Password123"}).json()["access_token"]


def test_dashboard_is_limited_to_authenticated_users_assignment(client_and_session):
    client, _ = client_and_session
    token = login(client, "rider.a@example.com")
    response = client.get("/api/v1/me/dashboard", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["route"]["name"] == "Route A"
    assert response.json()["vehicle"]["vehicle_number"] == "BUS-001"


def test_history_never_accepts_a_client_supplied_foreign_vehicle_id(client_and_session):
    client, _ = client_and_session
    token = login(client, "rider.a@example.com")
    response = client.get("/api/v1/me/history?vehicle_id=2", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["items"] == []
