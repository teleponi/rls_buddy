import uuid

import pytest
import requests


USER_SERVICE_URL = "http://localhost:8080"
TRACKING_SERVICE_URL = "http://localhost:8080"


def uniq():
    return str(uuid.uuid4())[:8]


@pytest.fixture(scope="function")
def create_user():
    """Fixture to create a user via the API."""

    email = "email_{}@example.com".format(uniq())
    user_data = {
        "name": "BobTestUser",
        "email": email,
        "password": "password123",
    }
    response = requests.post(f"{USER_SERVICE_URL}/users/", json=user_data)

    user_data["id"] = response.json()["id"]
    response.raise_for_status()
    return user_data, response.json()


@pytest.fixture(scope="function")
def get_auth_token(create_user):
    """Fixture to get the authentication token for the created user."""
    email = create_user[0]["email"]
    password = create_user[0]["password"]

    token_response = requests.post(
        f"{USER_SERVICE_URL}/token",
        data={"username": email, "password": password},
    )
    # token_response.raise_for_status()
    token = token_response.json().get("access_token")
    return token


@pytest.fixture(scope="function")
def create_symptoms_and_triggers(get_auth_token):
    """Fixture to create necessary symptoms and triggers via the API."""
    headers = {"Authorization": f"Bearer {get_auth_token}"}

    # Create symptoms
    symptoms = []
    for symptom_name in [uniq(), uniq()]:
        symptom_data = {"name": symptom_name}
        response = requests.post(
            f"{TRACKING_SERVICE_URL}/details/symptoms",
            json=symptom_data,
            headers=headers,
        )
        # response.raise_for_status()
        symptoms.append(response.json()["id"])

    # Create triggers
    triggers = []
    for trigger_name in [uniq(), uniq()]:
        trigger_data = {"name": trigger_name, "category": "food"}
        response = requests.post(
            f"{TRACKING_SERVICE_URL}/details/triggers",
            json=trigger_data,
            headers=headers,
        )
        response.raise_for_status()
        triggers.append(response.json()["id"])

    return symptoms, triggers


@pytest.fixture(scope="function")
def create_sleep_tracking(create_symptoms_and_triggers, get_auth_token):
    """Fixture to create sleep tracking entries via the API."""
    symptoms, _ = create_symptoms_and_triggers
    headers = {"Authorization": f"Bearer {get_auth_token}"}

    sleep_data = {
        "duration": 8,
        "date": "2024-09-10",
        "quality": "good",
        "symptoms": symptoms,
        "comment": "Good sleep",
    }
    url = f"{TRACKING_SERVICE_URL}/trackings/sleep"
    response = requests.post(
        url,
        headers=headers,
        json=sleep_data,
    )
    response.raise_for_status()
    return response.json()
