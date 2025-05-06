from ta_user_svc.models.base import get_db


def test_valid_registration(client):
    payload = {
        "email": "test@example.com",
        "password": "Password1",
        "nickname": "valid_nick"
    }
    response = client.post("/api/register", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["nickname"] == "valid_nick"
    assert data["role"] == "user"
    assert data["approved"] is False


def test_duplicate_email(client, db_session):
    # Override the get_db dependency to use the same db_session for both requests
    def override_get_db():
        yield db_session

    client.app.dependency_overrides[get_db] = override_get_db

    payload = {
        "email": "duplicate@example.com",
        "password": "Password1",
        "nickname": "nick1"
    }
    # First registration should succeed
    response1 = client.post("/api/register", json=payload)
    assert response1.status_code == 201, response1.text
    # Second registration with same email should fail
    response2 = client.post("/api/register", json=payload)
    assert response2.status_code == 409, response2.text
    # Reset the dependency override
    if get_db in client.app.dependency_overrides:
        del client.app.dependency_overrides[get_db]


def test_invalid_email(client):
    payload = {
        "email": "invalid-email",
        "password": "Password1",
        "nickname": "valid_nick"
    }
    response = client.post("/api/register", json=payload)
    assert response.status_code == 400


def test_invalid_password_length(client):
    payload = {
        "email": "test2@example.com",
        "password": "short",
        "nickname": "valid_nick"
    }
    response = client.post("/api/register", json=payload)
    assert response.status_code == 400


def test_invalid_password_no_letter(client):
    payload = {
        "email": "test3@example.com",
        "password": "12345678",
        "nickname": "valid_nick"
    }
    response = client.post("/api/register", json=payload)
    assert response.status_code == 400


def test_invalid_nickname_length(client):
    payload = {
        "email": "test4@example.com",
        "password": "Password1",
        "nickname": "abc"
    }
    response = client.post("/api/register", json=payload)
    assert response.status_code == 400


def test_invalid_nickname_characters(client):
    payload = {
        "email": "test5@example.com",
        "password": "Password1",
        "nickname": "invalid*nick"
    }
    response = client.post("/api/register", json=payload)
    assert response.status_code == 400
