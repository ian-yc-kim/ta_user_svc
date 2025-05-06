def test_logout_endpoint(client):
    response = client.get("/api/logout")
    assert response.status_code == 200
    assert response.json() == {"message": "Logout successful"}


def test_logout_endpoint_exception(client):
    # Use the force_error query parameter to simulate an exception in the logout endpoint
    response = client.get("/api/logout?force_error=true")
    # Expecting the endpoint to catch the exception and return a 500 error
    assert response.status_code == 500
    # Confirm that the error detail is returned
    json_resp = response.json()
    assert "detail" in json_resp
    assert json_resp["detail"] == "An error occurred while logging out"
