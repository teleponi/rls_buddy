import events
import pytest
import routers
from crud import create_user
from database import get_db
from fastapi.testclient import TestClient
from main import app
from schemes import UserCreate
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy_utils import create_database, database_exists


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
Base = declarative_base()


def mock_publish_user_delete_event(event: dict):
    pass


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

    app.dependency_overrides[
        routers.user.publish_user_delete_event
    ] = mock_publish_user_delete_event

    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def items(db):
    users = [
        {"name": "Grumpy", "email": "grumpy@cat.de", "password": "123456"},
        {"name": "Waldo", "email": "waldo@parillo.com", "password": "123456"},
    ]
    for user in users:
        create_user(db, UserCreate(**user))

    yield items
