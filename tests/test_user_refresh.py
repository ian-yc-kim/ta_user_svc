import os
import jwt
from datetime import datetime, timedelta
from fastapi import status

JWT_SECRET = os.getenv("JWT_SECRET", "mysecret")
ACCESS_TOKEN_EXPIRE_MINUTES = 10


def create_refresh_token(expiration_minutes: int, sub="test@example.com", nickname="testuser"):
    now = datetime.utcnow()
    payload = {
        "sub": sub,
        "nickname": nickname,
        "exp": now + timedelta(minutes=expiration_minutes)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def test_valid_refresh(client):
    refresh_token = create_refresh_token(expiration_minutes=30)
    response = client.post("/api/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data


def test_expired_refresh(client):
    refresh_token = create_refresh_token(expiration_minutes=-1)  # expired token
    response = client.post("/api/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert data.get("detail") == "Refresh token expired"


def test_invalid_refresh(client):
    # Malformed token
    response = client.post("/api/refresh", json={"refresh_token": "invalid.token.value"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert data.get("detail") == "Invalid refresh token"


def test_concurrent_refresh(client):
    # Simulate concurrent refresh calls
    refresh_token = create_refresh_token(expiration_minutes=30)
    responses = []
    for _ in range(5):
        responses.append(client.post("/api/refresh", json={"refresh_token": refresh_token}))
    for resp in responses:
        assert resp.status_code == status.HTTP_200_OK
        assert "access_token" in resp.json()
