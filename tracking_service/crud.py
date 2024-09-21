"""
This module provides the core CRUD (Create, Read, Update, Delete) operations
for managing trackings, symptoms, and triggers within the tracking service.

The functions in this module handle operations related to the Sleep and Day
tracking data, including validation, retrieval, and deletion. Exceptions are
defined to handle specific errors during the CRUD operations.

Functions:
    - get_tracking_by_id: Retrieve a tracking by its ID.
    - update_tracking: Update an existing tracking entry.
    - create_tracking: Create a new tracking entry.
    - delete_tracking: Delete a tracking entry by its ID.
    - delete_trackings_by_user: Delete all tracking entries associated with a user.
    - get_trackings_by_user: Retrieve trackings by user ID with optional date filters.
    - create_symptom: Create a new symptom entry.
    - get_symptoms: Retrieve symptom entries, optionally filtered by IDs.
    - create_trigger: Create a new trigger entry.
    - get_triggers: Retrieve trigger entries, optionally filtered by IDs.

Exceptions:
    - TrackingNotValidError: Raised when tracking data is not valid.
    - TrackingNotFoundError: Raised when a tracking entry is not found.
    - TrackingNotDeletedError: Raised when a tracking entry cannot be deleted.
    - TrackingNotUpdatedError: Raised when a tracking entry cannot be updated.
    - TrackingNotAllowedError: Raised when a user is not allowed to modify a tracking.
"""

import sys
from datetime import datetime

import models
import schemas as schemes
from loguru import logger
from sqlalchemy.orm import Session


logger.add(sys.stderr, format="{level} {time} {message}", colorize=True, level="INFO")


class TrackingNotValidError(Exception):
    pass


class TrackingNotFoundError(Exception):
    pass


class TrackingNotDeletedError(Exception):
    pass


class TrackingNotUpdatedError(Exception):
    pass


class TrackingNotAllowedError(Exception):
    pass


def get_model_by_attribute(attribute):
    d = {
        "symptoms": models.Symptom,
        "triggers": models.Trigger,
        "late_morning_symptoms": models.Symptom,
        "afternoon_symptoms": models.Symptom,
    }
    return d.get(attribute)


def add_values_to_model(db, db_tracking, tracking_data, attributes, update=False):
    for attr in attributes:
        values = tracking_data.pop(attr, None)
        if values is not None:
            attribute_list = [db.get(get_model_by_attribute(attr), v) for v in values]
            setattr(db_tracking, attr, attribute_list)

    if update:
        for key, value in tracking_data.items():
            setattr(db_tracking, key, value)


def get_tracking_by_id(
    db: Session, tracking_type: str, tracking_id: int
) -> models.Tracking | None:
    model = models.alchemy_model_factory(model_type=tracking_type)
    db_tracking = db.get(model, tracking_id)
    if not db_tracking:
        raise TrackingNotFoundError("Tracking not found")

    return db_tracking


def get_tracking_by_id_and_user(
    db: Session,
    tracking_type: str,
    tracking_id: int,
    user_id: int,
) -> models.Tracking:
    db_tracking = get_tracking_by_id(db, tracking_type, tracking_id)
    if db_tracking.user_id != user_id:
        raise TrackingNotAllowedError("User is not allowed to read this tracking")
    return db_tracking


def update_tracking(
    db: Session,
    tracking: schemes.BaseModel,
    tracking_type: str,
    tracking_id: int,
    user_id: int,
) -> models.Tracking:
    model = models.alchemy_model_factory(model_type=tracking_type)
    db_tracking = db.get(model, tracking_id)

    if not db_tracking:
        raise TrackingNotFoundError("Tracking not found")

    if db_tracking.user_id != user_id:
        raise TrackingNotAllowedError("User is not allowed to update this tracking")

    try:
        tracking_data = tracking.model_dump(exclude_unset=True)  # todo exclude_unset?
        add_values_to_model(
            db,
            db_tracking,
            tracking_data,
            [
                "symptoms",
                "triggers",
                "late_morning_symptoms",
                "afternoon_symptoms",
            ],
            update=True,
        )

        db.commit()
        db.refresh(db_tracking)
        return db_tracking
    except Exception as e:
        raise TrackingNotUpdatedError(f"Tracking could not be updated: {str(e)}")


def add_syptoms():
    pass


def create_tracking(
    db: Session,
    tracking: schemes.BaseModel,
    tracking_type: str,
    user_id: int,
) -> models.Tracking:
    """Create a new tracking."""
    model = models.alchemy_model_factory(model_type=tracking_type)
    tracking_data = tracking.model_dump(
        exclude={
            "symptoms",
            "triggers",
            "late_morning_symptoms",
            "afternoon_symptoms",
        }
    )
    tracking_data_org = tracking.model_dump()
    tracking_data["user_id"] = user_id

    try:
        db_tracking = model(**tracking_data)

        add_values_to_model(
            db,
            db_tracking,
            tracking_data_org,
            attributes=[
                "symptoms",
                "triggers",
                "late_morning_symptoms",
                "afternoon_symptoms",
            ],
        )

        db.add(db_tracking)
        db.commit()
        db.refresh(db_tracking)

        return db_tracking

    except Exception as e:
        logger.error(f"Tracking data not valid: {str(e)}")
        raise TrackingNotValidError(f"Tracking data not valid: {str(e)}")


def delete_tracking(
    db: Session,
    tracking_type: str,
    tracking_id: int,
    user_id: int,
) -> models.Tracking:
    """Delete a tracking."""
    model = models.alchemy_model_factory(model_type=tracking_type)
    db_tracking = db.get(model, tracking_id)

    if not db_tracking:
        raise TrackingNotFoundError("Tracking not found")

    if db_tracking.user_id != user_id:
        raise TrackingNotAllowedError("User is not allowed to delete this tracking")

    try:
        db.delete(db_tracking)
        db.commit()
    except Exception as e:
        raise TrackingNotDeletedError(f"Tracking could not be deleted: {str(e)}")

    return db_tracking


def delete_trackings_by_user(
    db: Session,
    user_id: int,
) -> None:
    """Delete all trackings by user_id."""
    try:
        db.query(models.Sleep).filter(models.Sleep.user_id == user_id).delete(
            synchronize_session=False
        )

        db.query(models.Day).filter(models.Day.user_id == user_id).delete(
            synchronize_session=False
        )
        db.commit()
        logger.info(f"Deleted all trackings for user {user_id} successfully.")

    except Exception as e:
        logger.warning(f"Deletion of trackings for user {user_id} not happended.")
        raise Exception(f"Fehler beim Löschen der Trackings: {str(e)}")


def get_trackings_by_user(
    db: Session,
    type: str,
    user_id: int,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[models.Tracking]:
    """Get trackings by user_id. Optionally filter by start and end dates."""
    model = models.alchemy_model_factory(model_type=type)
    queries = [model.user_id == user_id]

    if start_date and end_date:
        if type in ["sleep", "day"]:
            queries.append(model.date >= start_date)
            queries.append(model.date <= end_date)
        else:
            queries.append(model.timestamp >= start_date)
            queries.append(model.timestamp <= end_date)

    return db.query(model).filter(*queries).all()


def create_symptom(
    db: Session,
    symptom: schemes.SymptomCreate,
) -> schemes.Symptom:
    """Create a new symptom."""
    db_symptom = models.Symptom(**symptom.model_dump())
    db.add(db_symptom)
    db.commit()
    db.refresh(db_symptom)
    return db_symptom


def get_symptoms(db: Session, symptom_ids: list[int] = None) -> list[schemes.Symptom]:
    """Get symptoms. Specify symptom_ids to get specific symptoms."""
    if symptom_ids:
        symptoms = (
            db.query(models.Symptom).filter(models.Symptom.id.in_(symptom_ids)).all()
        )
    else:
        symptoms = db.query(models.Symptom).all()
    return symptoms


#
def create_trigger(
    db: Session,
    trigger: schemes.TriggerCreate,
) -> schemes.TriggerOut:
    """Create a new trigger."""
    db_trigger = models.Trigger(**trigger.model_dump())
    db.add(db_trigger)
    db.commit()
    db.refresh(db_trigger)
    return db_trigger


def get_triggers(
    db: Session, trigger_ids: list[int] = None
) -> list[schemes.TriggerOut]:
    """Get triggers. Specify trigger_ids to get specific triggers."""
    if trigger_ids:
        triggers = (
            db.query(models.Trigger).filter(models.Trigger.id.in_(trigger_ids)).all()
        )
    else:
        triggers = db.query(models.Trigger).all()
    return triggers
