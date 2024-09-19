import sys

import crud
import schemas as schemes
from database import get_db
from error_handler import format_sqlalchemy_error
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from schemas import Symptom, SymptomCreate
from sqlalchemy.orm import Session


logger.remove()  # remove default logger
logger.add(
    sys.stderr,
    format="<level>{level}:</level> {module} {message}",
    colorize=True,
    level="INFO",
)


router = APIRouter(prefix="/details/symptoms", tags=["Symptoms"])


@router.post(
    "/",
    response_model=Symptom,
    status_code=status.HTTP_201_CREATED,
)
def create_symptom(
    symptom: SymptomCreate,
    db: Session = Depends(get_db),
) -> schemes.Symptom:
    try:
        return crud.create_symptom(db, symptom)
    except Exception as e:
        error_message = format_sqlalchemy_error(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid data:" + error_message,
        )


@router.get("/", response_model=list[Symptom])
def get_symptoms(db: Session = Depends(get_db)) -> list[Symptom]:
    """public endpoint to get all symptoms."""
    return crud.get_symptoms(db)
