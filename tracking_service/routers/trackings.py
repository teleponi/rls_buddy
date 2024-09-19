import sys
from datetime import datetime

import crud
from auth import get_user_id_from_token
from database import get_db
from error_handler import format_sqlalchemy_error
from fastapi import APIRouter, Depends, HTTPException, Security, status
from loguru import logger
from schemas import DayCreate, DayOut, DayUpdate, SleepCreate, SleepOut, SleepUpdate
from sqlalchemy.orm import Session


logger.remove()  # remove default logger
logger.add(
    sys.stderr,
    format="<level>{level}:</level> {module} {message}",
    colorize=True,
    level="INFO",
)

TrackingOutSchemes = SleepOut | DayOut
TrackingCreateSchemes = SleepCreate | DayCreate
TrackingUpdateSchemes = SleepUpdate | DayUpdate

router = APIRouter(prefix="/trackings", tags=["Trackings"])


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def health_check_new(
    user_id: str = Security(get_user_id_from_token, scopes=["me"]),
) -> dict:
    if user_id:
        return {"user_id": user_id}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_trackings_by_user(
    db: Session = Depends(get_db),
    user_id: int = Security(get_user_id_from_token, scopes=["me"]),
) -> None:
    """Delete all trackings for the current user."""
    try:
        crud.delete_trackings_by_user(db, user_id)
    except Exception as e:
        logger.warning(f"Error deleting trackings: {e}")


@router.get("/me", response_model=list[TrackingOutSchemes])
async def get_trackings_by_user(
    type: str,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: Session = Depends(get_db),
    user_id: int = Security(get_user_id_from_token, scopes=["me"]),
    # user_id: int = Security(verify_token, scopes=["me"]),
) -> list[TrackingOutSchemes]:
    """Endpoint to get all trackings for the current user."""

    trackings = crud.get_trackings_by_user(db, type, user_id, start_date, end_date)
    if not trackings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {type} trackings found for this user",
        )
    return trackings


@router.post(
    "/day",
    response_model=TrackingOutSchemes,
    status_code=status.HTTP_201_CREATED,
)
def create_day_tracking(
    # tracking_type: str,
    tracking: DayCreate,
    db: Session = Depends(get_db),
    user_id: int = Security(get_user_id_from_token, scopes=["me"]),
) -> DayOut:
    tracking_type = "day"
    try:
        db_tracking = crud.create_tracking(db, tracking, tracking_type, user_id)
    except crud.TrackingNotValidError as e:
        error_message = format_sqlalchemy_error(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid data:" + error_message,
        )

    return db_tracking


@router.post(
    "/sleep",
    response_model=TrackingOutSchemes,
    status_code=status.HTTP_201_CREATED,
)
def create_sleep_tracking(
    # tracking_type: str,
    tracking: SleepCreate,
    db: Session = Depends(get_db),
    user_id: int = Security(get_user_id_from_token, scopes=["me"]),
) -> SleepOut:
    tracking_type = "sleep"
    try:
        db_tracking = crud.create_tracking(db, tracking, tracking_type, user_id)
    except crud.TrackingNotValidError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid data:" + str(e)
        )

    return db_tracking


@router.put("/{tracking_type}/{tracking_id}", response_model=TrackingOutSchemes)
def update_tracking(
    tracking_type: str,
    tracking_id: int,
    tracking: TrackingUpdateSchemes,
    db: Session = Depends(get_db),
    user_id: int = Security(get_user_id_from_token, scopes=["me"]),
) -> TrackingOutSchemes:
    """
    TrackingUpdate

    # todo: chek if user_id is allowded to update this tracking
    # todo: check if pydantic_model update is possible
    """
    try:
        return crud.update_tracking(db, tracking, tracking_type, tracking_id, user_id)
    except crud.TrackingNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tracking not found"
        )
    except crud.TrackingNotAllowedError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{e}")
    except crud.TrackingNotUpdatedError as e:
        logger.error(f"{e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")


@router.delete(
    "/{tracking_type}/{tracking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_tracking(
    tracking_type: str,
    tracking_id: int,
    db: Session = Depends(get_db),
    user_id: int = Security(get_user_id_from_token, scopes=["me"]),
) -> None:
    """Delete Tracking by tracking id and tracking type."""
    try:
        crud.delete_tracking(db, tracking_type, tracking_id, user_id)
    except crud.TrackingNotFoundError as e:
        logger.warning(f"{e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tracking could not be deleted: {e}",
        )
    except crud.TrackingNotAllowedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Tracking could not be deleted: {e}",
        )
    except (crud.TrackingNotDeletedError, Exception) as e:
        logger.error(f"{e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e}",
        )


@router.get("/{tracking_type}/{tracking_id}")
def get_tracking(
    tracking_type: str,
    tracking_id: int,
    db: Session = Depends(get_db),
    user_id: int = Security(get_user_id_from_token, scopes=["me"]),
) -> TrackingOutSchemes:
    """Get tracking by tracking id, user_id and tracking type."""
    try:
        return crud.get_tracking_by_id_and_user(
            db,
            tracking_type,
            tracking_id,
            user_id,
        )
    except crud.TrackingNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tracking could not be deleted: {e}",
        )
    except crud.TrackingNotAllowedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Tracking could not be deleted: {e}",
        )
