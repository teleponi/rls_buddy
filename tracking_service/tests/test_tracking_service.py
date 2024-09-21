import crud
import pytest
from enums import SleepQuality, TrackingType


SYMPTOMS_PATH = "/details/symptoms"
TRIGGER_PATH = "/details/triggers"


def test_create_symptom(client):
    response = client.post(
        SYMPTOMS_PATH,
        json={"name": "Restless Legs"},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Restless Legs"


def test_create_trigger(client):
    response = client.post(
        TRIGGER_PATH,
        json={"name": "Nikotin", "category": "food"},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Nikotin"


def test_cannot_create_trigger_with_same_name(client):
    response = client.post(
        TRIGGER_PATH,
        json={"name": "Nikotin", "category": "food"},
    )
    assert response.status_code == 201

    response = client.post(
        TRIGGER_PATH,
        json={"name": "Nikotin", "category": "food"},
    )
    assert response.status_code == 400


def test_cannot_create_trigger_with_wrong_category(client):
    response = client.post(
        TRIGGER_PATH,
        json={"name": "Nikotin", "category": "undefined"},
    )
    assert response.status_code == 400


def test_get_symptoms(items, client):
    response = client.get(SYMPTOMS_PATH)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_get_triggers(items, client):
    response = client.get(TRIGGER_PATH)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_create_day_tracking(items, client, token):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = client.post(
        "/trackings/day",
        json={
            "date": "2021-09-10",
            "comment": "Day well",
            "afternoon_symptoms": [1],
            "late_morning_symptoms": [2],
            "triggers": [1, 2],
        },
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["comment"] == "Day well"
    assert response.json()["user_id"] == 1
    assert response.json()["afternoon_symptoms"][0]["name"] == "Headache"
    assert response.json()["late_morning_symptoms"][0]["name"] == "Leg Pain"


def test_create_invalid_day_tracking(items, client, token):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = client.post(
        "/trackings/day",
        json={
            "date": "2021-09-10",
            "comment": "Day well",
            "afternoon_symptoms": [1, 99],  # invalid symptom id
            "late_morning_symptoms": [2],
            "triggers": [1, 2],
        },
        headers=headers,
    )
    assert response.status_code == 400
    assert "Tracking data not valid" in response.json()["detail"]


def test_create_sleep_tracking_invalid_data(items, client, token):
    # Create tracking with symptom
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = client.post(
        "/trackings/sleep",
        json={
            "duration": -8,
            "date": "2021-09-10",
            "quality": SleepQuality.GOOD,
            "comment": "Slept well",
            "symptoms": [1, 2],
        },
        headers=headers,
    )
    assert response.status_code == 400
    assert "Input should be greater" in response.json()["detail"][0]


def test_create_sleep_tracking(items, client, token):
    # Create symptom first
    response = client.post(
        SYMPTOMS_PATH,
        json={"name": "Arm Pain"},
    )
    symptom_id = response.json()["id"]

    # Create tracking with symptom
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = client.post(
        "/trackings/sleep",
        json={
            "duration": 8,
            "date": "2021-09-10",
            "quality": SleepQuality.GOOD,
            "comment": "Slept well",
            "symptoms": [symptom_id],
        },
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["duration"] == 8
    assert response.json()["user_id"] == 1
    assert response.json()["symptoms"][0]["name"] == "Arm Pain"


def test_get_sleep_trackings_by_user(items, client, token):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = client.get(
        "/trackings/me?type=sleep",
        headers=headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_get_empty_sleep_trackings_by_user(db, items, client, token):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    crud.delete_trackings_by_user(db, user_id=1)
    response = client.get(
        "/trackings/me?type=sleep",
        headers=headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "No sleep trackings found for this user"


def test_get_sleep_tracking(items, client, token):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = client.get(
        "trackings/sleep/1",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["comment"] == "Good sleep."


def test_get_day_tracking_not_found(items, client, token):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = client.get(
        "trackings/day/99",
        headers=headers,
    )
    assert response.status_code == 404


def test_get_sleep_tracking_not_allowed(items, client, token):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = client.get(
        "trackings/sleep/4",
        headers=headers,
    )
    assert response.status_code == 401


def test_get_day_trackings_by_user(items, client, token):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = client.get(
        "/trackings/me?type=day",
        headers=headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_get_wrong_type_trackings_by_user(items, client, token):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = client.get(
        "/trackings/me?type=undefined",
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid tracking type"


@pytest.mark.update
def test_update_tracking(db, items, client, token):
    # Create tracking first
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = client.post(
        "/trackings/sleep",
        json={
            "duration": 7,
            "date": "2022-09-11",
            "quality": SleepQuality.MODERATE,
            "comment": "Okay sleep",
            "symptoms": [1, 2],
        },
        headers=headers,
    )
    tracking_id = response.json()["id"]

    # Update the created tracking
    response = client.put(
        f"/trackings/sleep/{tracking_id}",
        json={
            "duration": 6,
            "quality": "bad",
            "symptoms": [],
            "comment": "bad sleep",
        },
        headers=headers,
    )
    tracking = crud.get_tracking_by_id(db, TrackingType.SLEEP, tracking_id)
    assert response.status_code == 200
    assert tracking.duration == 6
    assert response.json()["quality"] == SleepQuality.BAD
    assert response.json()["comment"] == "bad sleep"
    assert response.json()["symptoms"] == []


@pytest.mark.update
def test_update_tracking_not_found(db, items, client, token):
    # Create tracking first
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    tracking_id = 99

    # Update the created tracking
    response = client.put(
        f"/trackings/sleep/{tracking_id}",
        json={
            "duration": 6,
            "quality": "bad",
            "symptoms": [],
            "comment": "bad sleep",
        },
        headers=headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Tracking not found"


def test_update_not_owned_tracking(db, items, client, token):
    tracking_id = 4  # belongs to user 2, token is user 1
    headers = {"Authorization": f"Bearer {token}"}

    response = client.put(
        f"/trackings/sleep/{tracking_id}",
        json={
            "duration": 6,
            "quality": "bad",
            "symptoms": [],
            "comment": "bad sleep",
        },
        headers=headers,
    )

    assert response.status_code == 401
    tracking = crud.get_tracking_by_id(db, TrackingType.SLEEP, tracking_id)
    assert tracking.user_id == 2
    assert tracking.comment == "Good sleep."
    assert tracking.symptoms == crud.get_symptoms(db, [1])


def test_update_tracking_wrong_symptoms(db, items, client, token):
    tracking_id = 1
    headers = {"Authorization": f"Bearer {token}"}

    response = client.put(
        f"/trackings/sleep/{tracking_id}",
        json={
            "duration": 6,
            "quality": "bad",
            "symptoms": [99],
            "comment": "bad sleep",
        },
        headers=headers,
    )

    assert response.status_code == 400


def test_delete_trackings_from_user(db, items, client, token):
    headers = {"Authorization": f"Bearer {token}"}
    user_id = 1
    response = client.delete(
        "/trackings/me",
        headers=headers,
    )
    assert response.status_code == 204

    # check if items still in db
    sleeps = crud.get_trackings_by_user(db, TrackingType.SLEEP, user_id)
    assert len(sleeps) == 0

    days = crud.get_trackings_by_user(db, TrackingType.DAY, user_id)
    assert len(days) == 0


def test_delete_tracking(db, items, client, token):
    tracking_id = 1
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete(
        f"/trackings/sleep/{tracking_id}",
        headers=headers,
    )
    assert response.status_code == 204
    with pytest.raises(crud.TrackingNotFoundError):
        crud.get_tracking_by_id(db, TrackingType.SLEEP, tracking_id)


def test_delete_not_existing_tracking(db, items, client, token):
    tracking_id = 111
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete(
        f"/trackings/sleep/{tracking_id}",
        headers=headers,
    )

    assert response.status_code == 404
    with pytest.raises(crud.TrackingNotFoundError):
        crud.get_tracking_by_id(db, TrackingType.SLEEP, tracking_id)


def test_delete_not_owned_tracking(db, items, client, token):
    tracking_id = 4  # belongs to user 2, token is user 1
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete(
        f"/trackings/sleep/{tracking_id}",
        headers=headers,
    )

    tracking = crud.get_tracking_by_id(db, TrackingType.SLEEP, tracking_id)
    assert response.status_code == 401
    assert tracking.user_id == 2
