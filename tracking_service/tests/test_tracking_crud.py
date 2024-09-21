from datetime import datetime

import crud
import pytest
import schemas as schemes
from enums import SleepQuality, TrackingType, TriggerCategory
from httpx import AsyncClient
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError


def test_create_symptom_success(db):
    symptom_data = schemes.SymptomCreate(name="Restless Legs")
    symptom = crud.create_symptom(db, symptom_data)
    assert symptom.id is not None
    assert symptom.name == "Restless Legs"


def test_create_trigger_success(db):
    trigger_data = schemes.TriggerCreate(
        name="Nikotin",
        category=TriggerCategory.FOOD,
    )
    trigger = crud.create_trigger(db, trigger_data)
    assert trigger.id is not None
    assert trigger.name == "Nikotin"


def test_cannot_create_trigger_same_name_twice(db):
    trigger_data = schemes.TriggerCreate(
        name="Nikotin",
        category=TriggerCategory.FOOD,
    )
    trigger = crud.create_trigger(db, trigger_data)
    trigger_data = schemes.TriggerCreate(
        name="Nikotin",
        category=TriggerCategory.FOOD,
    )
    with pytest.raises(IntegrityError):
        crud.create_trigger(db, trigger_data)


def test_delete_trackings_by_user(items, db):
    """Test, ob alle Schlaf-Trackings eines Benutzers gelöscht werden können."""
    user_id = 1
    trackings = crud.get_trackings_by_user(db, TrackingType.SLEEP, user_id)
    assert len(trackings) > 0

    trackings = crud.get_trackings_by_user(db, TrackingType.DAY, user_id)
    assert len(trackings) > 0

    crud.delete_trackings_by_user(db, user_id)
    trackings = crud.get_trackings_by_user(db, TrackingType.SLEEP, user_id)
    assert len(trackings) == 0


def test_create_day_success(items, db):
    day_data = schemes.DayCreate(
        date=datetime(2024, 11, 7),
        comment="Slept well",
        afternoon_symptoms=[1, 2],
        late_morning_symptoms=[1, 2],
        triggers=[1, 2],
    )
    user_id = 1
    day = crud.create_tracking(db, day_data, TrackingType.DAY, user_id)
    assert day.id is not None
    assert day.user_id == user_id
    assert day.date == datetime(2024, 11, 7)
    assert day.comment == "Slept well"
    assert day.afternoon_symptoms == crud.get_symptoms(db, [1, 2])
    assert day.late_morning_symptoms == crud.get_symptoms(db, [1, 2])
    assert day.triggers == crud.get_triggers(db, [1, 2])


def test_update_day_success(items, db):
    # Create a day entry first
    day_id = 1
    user_id = 1

    # Update the created day entry
    updated_day_data = schemes.DayUpdate(
        comment="Bad day day",
        symptoms=[2],
        afternoon_symptoms=[1],
        late_morning_symptoms=[1],
        triggers=[],
    )
    updated_day = crud.update_tracking(
        db, updated_day_data, TrackingType.DAY, day_id, user_id
    )
    assert updated_day.id == day_id
    assert updated_day.comment == "Bad day day"
    assert updated_day.afternoon_symptoms == crud.get_symptoms(db, [1])
    assert updated_day.late_morning_symptoms == crud.get_symptoms(db, [1])
    assert updated_day.triggers == []


def test_create_sleep_success(items, db):
    sleep_data = schemes.SleepCreate(
        duration=8,
        date=datetime(2024, 11, 7),
        quality=SleepQuality.GOOD,
        comment="Slept well",
        symptoms=[1, 2],
    )
    user_id = 1
    sleep = crud.create_tracking(db, sleep_data, TrackingType.SLEEP, user_id)
    assert sleep.id is not None
    assert sleep.user_id == user_id
    assert sleep.duration == 8
    assert sleep.date == datetime(2024, 11, 7)
    assert sleep.quality == SleepQuality.GOOD
    assert sleep.comment == "Slept well"
    assert sleep.symptoms == crud.get_symptoms(db, [1, 2])


def test_update_sleep_success(items, db):
    # Create a sleep entry first
    sleep_data = schemes.SleepCreate(
        duration=7,
        date=datetime(2021, 9, 11),
        quality=SleepQuality.MODERATE,
        comment="Okay sleep",
        symptoms=[1],
    )
    user_id = 1
    sleep = crud.create_tracking(db, sleep_data, TrackingType.SLEEP, user_id)
    sleep_id = sleep.id

    # Update the created sleep entry
    updated_sleep_data = schemes.SleepUpdate(
        duration=6,
        quality=SleepQuality.BAD,
        comment="Bad sleep",
        symptoms=[2],
    )
    updated_sleep = crud.update_tracking(
        db, updated_sleep_data, TrackingType.SLEEP, sleep_id, user_id
    )
    assert updated_sleep.id == sleep_id
    assert updated_sleep.duration == 6
    assert updated_sleep.quality == SleepQuality.BAD
    # assert updated_sleep.comment == "Bad sleep"
    for updated_symptom, expected_symptom in zip(
        updated_sleep.symptoms, crud.get_symptoms(db, symptom_ids=[2])
    ):
        assert updated_symptom.id == expected_symptom.id
        assert updated_symptom.name == expected_symptom.name


def test_update_sleep_not_found(db):
    updated_sleep_data = schemes.SleepUpdate(
        duration=6, quality=SleepQuality.BAD, symptoms=[], comment=""
    )
    with pytest.raises(crud.TrackingNotFoundError):
        crud.update_tracking(
            db, updated_sleep_data, TrackingType.SLEEP, 999, 1
        )  # 999 Non-existent ID


def test_update_day_not_exists(db):
    updated_day_data = schemes.DayUpdate(
        comment="Bad day day",
        symptoms=[2],
        afternoon_symptoms=[1],
        late_morning_symptoms=[1],
        triggers=[],
    )

    with pytest.raises(crud.TrackingNotFoundError):
        crud.update_tracking(
            db, updated_day_data, TrackingType.DAY, 999, 1
        )  # 999 Non-existent ID


def test_get_trackings_by_user_success(items, db):
    """Test, ob alle Schlaf-Trackings eines Benutzers abgerufen werden können."""
    user_id = 1

    start_date = None
    end_date = None
    trackings = crud.get_trackings_by_user(
        db, TrackingType.SLEEP, user_id, start_date, end_date
    )
    assert len(trackings) > 0
    assert trackings[0].user_id == user_id


def test_get_sleeps_by_user_dates(items, db):
    """Test sleeps by user with start and end dates."""

    user_id = 1

    # in conftest.py are two sleep entries for these dates
    start_date = datetime(2024, 9, 10)
    end_date = datetime(2024, 9, 11)
    trackings = crud.get_trackings_by_user(
        db, TrackingType.SLEEP, user_id, start_date, end_date
    )
    assert len(trackings) == 2
    assert trackings[0].user_id == user_id


@pytest.mark.parametrize(
    "duration, date, quality, symptoms",
    [
        (-1, datetime(2024, 9, 20), SleepQuality.GOOD, [1, 2]),  # Invalid duration
        (8, None, SleepQuality.GOOD, [1, 2]),  # Invalid date (None)
        (8, "invalid-date", SleepQuality.GOOD, [1, 2]),  # Invalid date format
        (8, datetime(2024, 9, 21), "excellent", [1, 2]),  # Invalid quality
        (8, datetime(2024, 9, 22), SleepQuality.GOOD, [999]),  # Invalid symptom ID
    ],
)
def test_create_sleep_invalid_data(duration, date, quality, symptoms, db, items):
    user_id = 1

    with pytest.raises((crud.TrackingNotValidError, ValidationError)):
        sleep_data = schemes.SleepCreate(
            duration=duration,
            date=date,
            quality=quality,
            comment="Slept well",
            symptoms=symptoms,
        )
        crud.create_tracking(db, sleep_data, TrackingType.SLEEP, user_id)
