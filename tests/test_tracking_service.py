"""
This module contains system tests for the tracking service.

The following tests are included:
- test_create_day_tracking: Tests the creation of a day tracking entryself.
- test_create_sleep_tracking: Tests the creation of a sleep tracking entry.
"""

import requests


API_TEST_GATEWAY_URL = "http://127.0.0.1:8080"


def test_create_day_tracking(get_auth_token, create_symptoms_and_triggers):
    token = get_auth_token  # The token is obtained from the fixture
    headers = {"Authorization": f"Bearer {token}"}
    symptoms, triggers = create_symptoms_and_triggers  # Use

    response = requests.post(
        f"{API_TEST_GATEWAY_URL}/trackings/day",
        json={
            "date": "2024-09-10",
            "late_morning_symptoms": symptoms,
            "afternoon_symptoms": symptoms,
            "triggers": triggers,
            "comment": "Feeling good",
        },
        headers=headers,
    )
    assert response.status_code == 201
    assert [i["id"] for i in response.json()["late_morning_symptoms"]] == symptoms
    assert [i["id"] for i in response.json()["afternoon_symptoms"]] == symptoms
    assert [i["id"] for i in response.json()["triggers"]] == triggers


def test_create_sleep_tracking(get_auth_token, create_symptoms_and_triggers):
    token = get_auth_token  # The token is obtained from the fixture
    headers = {"Authorization": f"Bearer {token}"}

    symptoms, _ = create_symptoms_and_triggers  # Use the created symptoms

    response = requests.post(
        f"{API_TEST_GATEWAY_URL}/trackings/sleep",
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
