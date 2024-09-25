import uuid

import pytest
import requests


API_TEST_GATEWAY_URL = "http://127.0.0.1:8080"


def uniq():
    return str(uuid.uuid4())[:8]


def test_create_user():
    """
    Test user creation via the API gateway.

    Generates a random email and username, then attempts to create a
    user. Asserts that the response status code is 201, indicating
    successful creation.
    """
    email = "email_{}@example.com".format(uniq().replace("-", ""))
    password = "password123"
    response = requests.post(
        f"{API_TEST_GATEWAY_URL}/users/",
        json={
            "name": "TestUser" + uniq().replace("-", ""),
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 201


def test_get_token_without_api_gateway(create_user):
    """
    Test if user service is unreachable from outside.

    Assumes a connection error occurs when trying to access the user
    service directly, bypassing the API gateway.
    """

    illegal_user_service_url = "http://user-service:8001"  # not reachable from outside
    email = create_user[0]["email"]
    password = create_user[0]["password"]

    with pytest.raises(requests.exceptions.ConnectionError):
        requests.post(
            f"{illegal_user_service_url}/token",
            data={"username": email, "password": password},
        )


def test_cannot_get_token_with_invalid_credentials(create_user):
    """
    Test if token request fails with invalid credentials.

    Attempts to get a token with incorrect password.
    Asserts status code is 401 and 'access_token' is not in the response.
    """

    email = create_user[0]["email"]
    password = "invalid_password"

    response = requests.post(
        f"{API_TEST_GATEWAY_URL}/token",
        data={"username": email, "password": password},
    )
    assert response.status_code == 401
    assert "access_token" not in response.json()


def test_get_token(create_user):
    """
    Test retrieving a token.

    Asserts that the status code is 200 and the response contains 'access_token'.
    """

    email = create_user[0]["email"]
    password = create_user[0]["password"]

    response = requests.post(
        f"{API_TEST_GATEWAY_URL}/token",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_delete_user(create_user, create_sleep_tracking):
    email = create_user[0]["email"]
    password = create_user[0]["password"]

    token_response = requests.post(
        f"{API_TEST_GATEWAY_URL}/token",
        data={"username": email, "password": password},
    )
    token_response.raise_for_status()
    token = token_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    trackings_response = requests.get(
        f"{API_TEST_GATEWAY_URL}/trackings/me?type=sleep", headers=headers
    )

    # Verify the sleep tracking was created
    assert trackings_response.status_code == 200
    assert len(trackings_response.json()) > 0

    # Delete the user
    delete_response = requests.delete(
        f"{API_TEST_GATEWAY_URL}/users/me", headers=headers
    )
    assert delete_response.status_code == 204

    # Verify the user was deleted (401 Unauthorized)
    response = requests.get(f"{API_TEST_GATEWAY_URL}/users/me", headers=headers)
    assert response.status_code == 401

    # Verify the trackings was deleted
    params = {"user_id": create_user[0]["id"]}

    trackings_response = requests.get(
        f"{API_TEST_GATEWAY_URL}/trackings/",
        headers=headers,
        params=params,
    )

    assert trackings_response.status_code == 404
