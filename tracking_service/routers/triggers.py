import crud
from database import get_db
from error_handler import format_sqlalchemy_error
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from schemas import TriggerCreate, TriggerOut
from sqlalchemy.orm import Session


router = APIRouter(prefix="/details/triggers", tags=["Triggers"])


@router.post(
    "/",
    response_model=TriggerOut,
    status_code=status.HTTP_201_CREATED,
)
def create_trigger(
    trigger: TriggerCreate,
    db: Session = Depends(get_db),
) -> TriggerOut:
    """public endpoint to create a trigger."""
    try:
        return crud.create_trigger(db, trigger)
    except Exception as e:
        error_message = format_sqlalchemy_error(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid data:" + error_message,
        )


@router.get("/", response_model=list[TriggerOut])
def get_triggers(db: Session = Depends(get_db)) -> list[TriggerOut]:
    """public endpoint to get all triggers."""
    return crud.get_triggers(db)
