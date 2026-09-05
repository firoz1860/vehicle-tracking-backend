def test_login_returns_jwt_for_valid_credentials(client_and_session):
    client, _ = client_and_session
    response = client.post("/api/v1/auth/login", json={"email": "rider.a@example.com", "password": "Password123"})

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_rejects_wrong_password(client_and_session):
    client, _ = client_and_session
    response = client.post("/api/v1/auth/login", json={"email": "rider.a@example.com", "password": "WrongPass123"})

    assert response.status_code == 401
