"""
Data Models for Tracking Service

This module defines the SQLAlchemy ORM models used in the Tracking Service
to represent the core entities for tracking user data related to sleep
and daily activities. The models establish relationships between users,
tracking entries, symptoms, and triggers.

Key Entities:
- Tracking: An abstract base model representing shared attributes between
  different types of tracking entries, including user ID, timestamps,
  and update times.
- Sleep: Represents sleep data with duration, quality, and associated
  symptoms.
- Day: Tracks daily activities, including triggers and symptoms that occur
  during the day.
- Symptom: Represents a specific symptom that can be associated with sleep
  or daily tracking entries.
- Trigger: Represents a specific trigger that can be associated with
  daily activities.

The models define relationships such as many-to-many associations between
symptoms, triggers, and tracking entries. Constraints are enforced to
ensure data consistency, including uniqueness on specific combinations
such as user_id and date for sleep and day entries.

Author: Bernd Fischer, 2024
"""

from database import Base
from enums import SleepQuality, TriggerCategory
from fastapi import HTTPException
from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy import ForeignKey, Integer, String, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


# Association table for the many-to-many relationship
sleep_symptom_association = Table(
    "sleep_symptom_association",
    Base.metadata,
    Column("sleep_id", Integer, ForeignKey("sleeps.id", ondelete="CASCADE")),
    Column("symptom_id", Integer, ForeignKey("symptoms.id")),
)

day_trigger_association = Table(
    "day_trigger_association",
    Base.metadata,
    Column("day_id", Integer, ForeignKey("days.id", ondelete="CASCADE")),
    Column("trigger_id", Integer, ForeignKey("triggers.id")),
)

late_morning_symptom_association = Table(
    "late_morning_symptom_association",
    Base.metadata,
    Column("day_id", Integer, ForeignKey("days.id", ondelete="CASCADE")),
    Column("symptom_id", Integer, ForeignKey("symptoms.id")),
)

afternoon_symptom_association = Table(
    "afternoon_symptom_association",
    Base.metadata,
    Column("day_id", Integer, ForeignKey("days.id", ondelete="CASCADE")),
    Column("symptom_id", Integer, ForeignKey("symptoms.id")),
)


class Tracking(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())


class Trigger(Base):
    """Table for triggers."""

    __tablename__ = "triggers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    category = Column(SQLAEnum(TriggerCategory), nullable=False)


class Symptom(Base):
    """Table for standard RLS symptoms."""

    __tablename__ = "symptoms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)


class Day(Tracking):
    """Table for daily activities and trigger tracking."""

    __tablename__ = "days"

    date = Column(DateTime, index=True)
    comment = Column(String, nullable=True)
    triggers = relationship(
        "Trigger",
        secondary=day_trigger_association,
        passive_deletes=True,
    )
    late_morning_symptoms = relationship(
        "Symptom",
        secondary=late_morning_symptom_association,
        passive_deletes=True,
    )
    afternoon_symptoms = relationship(
        "Symptom",
        secondary=afternoon_symptom_association,
        passive_deletes=True,
    )
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "date",
            name="day_uix_email_date",
        ),
    )


class Sleep(Tracking):
    """Table for daily Sleep Quality tracking."""

    __tablename__ = "sleeps"

    duration = Column(Integer)
    date = Column(DateTime, index=True)
    quality = Column(SQLAEnum(SleepQuality), nullable=False)
    comment = Column(String, nullable=True)
    symptoms = relationship(
        "Symptom",
        secondary=sleep_symptom_association,
        back_populates="sleeps",
        passive_deletes=True,
    )
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "date",
            name="sleep_uix_email_date",
        ),
    )


# reverse relationship
Symptom.sleeps = relationship(
    "Sleep",
    secondary=sleep_symptom_association,
    back_populates="symptoms",
)


def alchemy_model_factory(model_type: str) -> Tracking:
    models = {
        "day": Day,
        "sleep": Sleep,
    }
    try:
        return models[model_type]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid tracking type")
