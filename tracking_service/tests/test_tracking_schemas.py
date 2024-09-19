from datetime import datetime

import pytest
from enums import SleepQuality
from pydantic import ValidationError
from schemas import (
    SleepCreate,
    SleepOut,
    SleepUpdate,
    Symptom,
    SymptomCreate,
    TrackingCreate,
    TrackingOut,
    TrackingUpdate,
)


def test_symptom_create_success():
    symptom = SymptomCreate(name="Leg Pain")
    assert symptom.name == "Leg Pain"


def test_symptom_create_invalid():
    with pytest.raises(ValidationError):
        SymptomCreate(name=123)  # Name should be a string


def test_symptom_success():
    symptom = Symptom(id=1, name="Leg Pain")
    assert symptom.id == 1
    assert symptom.name == "Leg Pain"


def test_symptom_invalid():
    with pytest.raises(ValidationError):
        Symptom(id="one", name="Leg Pain")  # ID should be an int


def test_sleep_create_success():
    sleep = SleepCreate(
        duration=8,
        date=datetime(2024, 9, 10, 10, 0),
        quality=SleepQuality.GOOD,
        symptoms=[1, 2, 3],
        comment="Good sleep.",
    )
    assert sleep.duration == 8
    assert sleep.date == datetime(2024, 9, 10, 10, 0)
    assert sleep.quality == SleepQuality.GOOD
    assert sleep.symptoms == [1, 2, 3]


def test_sleep_create_invalid_duration():
    with pytest.raises(ValidationError):
        SleepCreate(
            duration=-1,  # Duration should be positive
            date=datetime(2024, 9, 10, 10, 0),
            quality=SleepQuality.GOOD,
            symptoms=[1, 2, 3],
            comment="Good sleep.",
        )


def test_sleep_create_invalid_quality():
    with pytest.raises(ValidationError):
        SleepCreate(
            duration=8,
            date=datetime(2024, 9, 10, 10, 0),
            quality="excellent",  # Quality should be from SleepQuality enum
            symptoms=[1, 2, 3],
            comment="Okay sleep",
        )


def test_sleep_update_success():
    sleep_update = SleepUpdate(
        duration=7,
        quality=SleepQuality.MODERATE,
        symptoms=[1],
        comment="Okay sleep",
    )
    assert sleep_update.duration == 7
    assert sleep_update.quality == SleepQuality.MODERATE
    assert sleep_update.symptoms == [1]


def test_sleep_update_invalid_duration():
    with pytest.raises(ValidationError):
        SleepUpdate(
            duration=-5,  # Duration should be positive
            quality=SleepQuality.MODERATE,
            symptoms=[1],
        )


def test_sleep_out_success():
    sleep_out = SleepOut(
        id=1,
        user_id=1,
        timestamp=datetime(2024, 9, 10, 10, 0),
        duration=8,
        date=datetime(2024, 9, 10, 10, 0),
        quality=SleepQuality.GOOD,
        comment="Okay sleep",
        symptoms=[Symptom(id=1, name="Leg Pain")],
    )
    assert sleep_out.id == 1
    assert sleep_out.user_id == 1
    assert sleep_out.timestamp == datetime(2024, 9, 10, 10, 0)
    assert sleep_out.duration == 8
    assert sleep_out.date == datetime(2024, 9, 10, 10, 0)
    assert sleep_out.quality == SleepQuality.GOOD
    assert len(sleep_out.symptoms) == 1
    assert sleep_out.symptoms[0].id == 1
    assert sleep_out.symptoms[0].name == "Leg Pain"


def test_tracking_out_success():
    tracking_out = TrackingOut(id=1, user_id=1, timestamp=datetime(2024, 9, 10, 10, 0))
    assert tracking_out.id == 1
    assert tracking_out.user_id == 1
    assert tracking_out.timestamp == datetime(2024, 9, 10, 10, 0)
