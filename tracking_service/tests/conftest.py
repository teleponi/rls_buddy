import os
from datetime import datetime, timedelta, timezone

import auth
import jwt
import pytest
import schemas as schemes
from crud import create_symptom, create_tracking, create_trigger
from database import get_db
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from fastapi.testclient import TestClient
from main import app, start_consuming_events
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy_utils import create_database, database_exists


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
Base = declarative_base()

SECRET_KEY = "mysecretkeyo"
ALGORITHM = "HS256"
TEST_USER_ID = 1

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def mock_get_user_id_from_token(scopes: SecurityScopes, token=Depends(oauth2_scheme)):
    return TEST_USER_ID


def mock_consume_events():
    pass


@pytest.fixture(scope="session")
def token():
    """Simulate token generation for non-user services."""
    data = {
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        "sub": "1",
        "scopes": ["me", "items"],
    }
    yield jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    if not database_exists:
        create_database(engine.url)

    Base.metadata.create_all(bind=engine)
    yield engine


@pytest.fixture(scope="function")
def db(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    db = Session(bind=connection)
    yield db
    db.close()
    transaction.rollback()
    db.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[auth.get_user_id_from_token] = mock_get_user_id_from_token
    app.dependency_overrides[start_consuming_events] = mock_consume_events

    with TestClient(app) as c:
        yield c


@pytest.fixture
def items(db):
    user_id = 1
    symptoms = [
        {"name": "Headache"},
        {"name": "Leg Pain"},
        {"name": "Restless Legs"},
    ]
    triggers = [
        {"name": "Süßigkeiten", "category": "food"},
        {"name": "Stress", "category": "lifestyle"},
    ]
    sleeps = [
        {
            "duration": 8,
            "date": "2024-09-10",
            "quality": "good",
            "symptoms": [1],
            "comment": "Good sleep.",
        },
        {
            "duration": 6,
            "date": "2024-09-11",
            "quality": "bad",
            "symptoms": [2, 3],
            "comment": "Bad sleep.",
        },
        {
            "duration": 7,
            "date": "2024-09-12",
            "quality": "good",
            "symptoms": [1, 3],
            "comment": "",
        },
    ]

    days = [
        {
            "date": "2021-10-01",
            "comment": "godd day",
            "triggers": [1],
            "late_morning_symptoms": [1, 2],
            "afternoon_symptoms": [1, 2, 3],
        },
        {
            "date": "2021-10-02",
            "comment": "special day",
            "triggers": [1, 2],
            "late_morning_symptoms": [1, 2],
            "afternoon_symptoms": [1, 3],
        },
        {
            "date": "2021-10-03",
            "triggers": [1, 2],
            "comment": "test day",
            "late_morning_symptoms": [2, 3],
            "afternoon_symptoms": [],
        },
        {
            "date": "2021-10-04",
            "comment": "perfect day",
            "triggers": [1, 2],
            "late_morning_symptoms": [],
            "afternoon_symptoms": [1],
        },
        {
            "date": "2021-10-05",
            "comment": "bad day",
            "triggers": [1, 2],
            "late_morning_symptoms": [2],
            "afternoon_symptoms": [2],
        },
    ]

    for symptom in symptoms:
        create_symptom(db, schemes.SymptomCreate(**symptom))

    for trigger in triggers:
        create_trigger(db, schemes.TriggerCreate(**trigger))

    for tracking in sleeps:
        create_tracking(db, schemes.SleepCreate(**tracking), "sleep", user_id)

    for tracking in days:
        create_tracking(db, schemes.DayCreate(**tracking), "day", user_id)

    # sleep by user 2, id 4
    create_tracking(db, schemes.SleepCreate(**sleeps[0]), "sleep", 2)

    yield items
