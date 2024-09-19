import crud
import pytest
from enums import SleepQuality, TrackingType


SYMPTOMS_PATH = "/details/symptoms"


def test_create_symptom(client):
    response = client.post(
        SYMPTOMS_PATH,
        json={"name": "Restless Legs"},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Restless Legs"


def test_get_symptoms(items, client):
    response = client.get(SYMPTOMS_PATH)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_create_tracking(items, client, token):
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


def test_get_day_trackings_by_user(items, client, token):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = client.get(
        "/trackings/me?type=day",
        headers=headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


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


# @pytest.mark.skip
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
