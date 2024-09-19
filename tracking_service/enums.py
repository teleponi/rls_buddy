from enum import StrEnum


class TriggerCategory(StrEnum):
    FOOD = "food"
    ENVIRONMENT = "environment"
    LIFESTYLE = "lifestyle"
    EMOTION = "emotion"
    OTHER = "other"


class TrackingType(StrEnum):
    SLEEP = "sleep"
    DAY = "day"


class SleepQuality(StrEnum):
    BAD = "bad"
    MODERATE = "moderate"
    GOOD = "good"
