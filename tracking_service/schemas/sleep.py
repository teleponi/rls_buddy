from datetime import datetime

from enums import SleepQuality
from pydantic import BaseModel, ConfigDict, PositiveInt

from .basic import TrackingCreate, TrackingOut, TrackingUpdate
from .symptoms import Symptom


class SleepCreate(TrackingCreate):
    duration: PositiveInt
    date: datetime
    quality: SleepQuality
    comment: str | None
    symptoms: list[int] | None


class SleepUpdate(TrackingUpdate):
    duration: PositiveInt
    quality: SleepQuality
    symptoms: list[int] | None
    comment: str


class SleepOut(TrackingOut):
    duration: PositiveInt
    date: datetime
    quality: SleepQuality
    symptoms: list[Symptom]
    comment: str
