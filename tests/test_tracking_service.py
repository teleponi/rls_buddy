import pytest
import requests


TRACKING_SERVICE_URL = "http://localhost:8080"


def test_create_sleep_tracking(get_auth_token, create_symptoms_and_triggers):
    token = get_auth_token  # The token is obtained from the fixture
    headers = {"Authorization": f"Bearer {token}"}

    symptoms, _ = create_symptoms_and_triggers  # Use the created symptoms

    response = requests.post(
        f"{TRACKING_SERVICE_URL}/trackings/sleep",
        json={
            "duration": 8,
            "date": "2024-09-10",
            "quality": "good",
            "comment": "Slept well",
            "symptoms": symptoms,  # Use the symptoms created via the fixture
        },
        headers=headers,
    )

    assert response.status_code == 201
    assert response.json()["duration"] == 8
    assert response.json()["quality"] == "good"
    assert response.json()["comment"] == "Slept well"
    assert [i["id"] for i in response.json()["symptoms"]] == symptoms
