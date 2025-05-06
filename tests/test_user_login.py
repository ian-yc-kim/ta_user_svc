import os
from datetime import datetime, timedelta

import jwt
import pytest
from fastapi import status
from passlib.context import CryptContext

from ta_user_svc.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = os.getenv("JWT_SECRET", "mysecret")


def test_successful_login(client, db_session):
    # Create a user with approved=True and hashed password
    password = "password123"
    hashed = pwd_context.hash(password)
    user = User(email="test@example.com", passhash=hashed, nickname="Tester", approved=True)
    session = db_session
    session.add(user)
    session.commit()

    response = client.post("/api/login", json={"email": "test@example.com", "password": password})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

    # Validate token payload for access token
    access_payload = jwt.decode(data["access_token"], JWT_SECRET, algorithms=["HS256"])
    assert access_payload.get("sub") == "test@example.com"
    assert access_payload.get("nickname") == "Tester"


def test_invalid_password(client, db_session):
    # Create a user with approved=True and known password
    password = "password123"
    hashed = pwd_context.hash(password)
    user = User(email="wrongpass@example.com", passhash=hashed, nickname="Tester", approved=True)
    session = db_session
    session.add(user)
    session.commit()

    response = client.post("/api/login", json={"email": "wrongpass@example.com", "password": "wrongpassword"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_unapproved_user(client, db_session):
    # Create a user that is not approved
    password = "password123"
    hashed = pwd_context.hash(password)
    user = User(email="unapproved@example.com", passhash=hashed, nickname="Tester", approved=False)
    session = db_session
    session.add(user)
    session.commit()

    response = client.post("/api/login", json={"email": "unapproved@example.com", "password": password})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json().get("detail") == "User not approved"


def test_invalid_email_format(client):
    # Email format invalid should trigger validation error (422)
    response = client.post("/api/login", json={"email": "invalidemail", "password": "password123"})
    assert response.status_code == 422


def test_missing_fields(client):
    # Missing password field should trigger validation error (422)
    response = client.post("/api/login", json={"email": "test@example.com"})
    assert response.status_code == 422
