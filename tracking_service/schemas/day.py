from datetime import datetime

from .basic import TrackingCreate, TrackingOut, TrackingUpdate
from .symptoms import Symptom as SymptomOut
from .triggers import TriggerOut


class DayCreate(TrackingCreate):
    """Schema for creating a new day entry."""

    date: datetime
    comment: str | None
    triggers: list[int] | None
    late_morning_symptoms: list[int] | None
    afternoon_symptoms: list[int] | None


class DayUpdate(TrackingUpdate):
    """Schema for updating an existing day entry."""

    comment: str | None
    triggers: list[int] | None
    late_morning_symptoms: list[int] | None
    afternoon_symptoms: list[int] | None


class DayOut(TrackingOut):
    """Schema for returning a day entry."""

    date: datetime
    comment: str
    triggers: list[TriggerOut]
    late_morning_symptoms: list[SymptomOut]
    afternoon_symptoms: list[SymptomOut]
