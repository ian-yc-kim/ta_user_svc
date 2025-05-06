def test_valid_registration(client):
    payload = {
        "email": "test@example.com",
        "password": "Password1",
        "nickname": "valid_nick"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["nickname"] == "valid_nick"
    assert data["role"] == "user"
    assert data["approved"] is False


def test_duplicate_email(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "Password1",
        "nickname": "nick1"
    }
    # First registration should succeed
    response1 = client.post("/register", json=payload)
    assert response1.status_code == 201, response1.text
    # Second registration with same email should fail
    response2 = client.post("/register", json=payload)
    assert response2.status_code == 409, response2.text


def test_invalid_email(client):
    payload = {
        "email": "invalid-email",
        "password": "Password1",
        "nickname": "valid_nick"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 400


def test_invalid_password_length(client):
    payload = {
        "email": "test2@example.com",
        "password": "short",
        "nickname": "valid_nick"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 400


def test_invalid_password_no_letter(client):
    payload = {
        "email": "test3@example.com",
        "password": "12345678",
        "nickname": "valid_nick"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 400


def test_invalid_nickname_length(client):
    payload = {
        "email": "test4@example.com",
        "password": "Password1",
        "nickname": "abc"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 400


def test_invalid_nickname_characters(client):
    payload = {
        "email": "test5@example.com",
        "password": "Password1",
        "nickname": "invalid*nick"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 400
