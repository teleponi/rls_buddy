import pytest
from crud import (
    UserExistsError,
    UserNotDeletedError,
    UserNotFoundError,
    UserNotUpdatedError,
    UserNotValidError,
    create_user,
    delete_user,
    get_user,
    get_user_by_email,
    get_user_by_id,
    update_user,
)
from pydantic import ValidationError
from schemes import UserCreate, UserOut, UserUpdate
from sqlalchemy import exc
from sqlalchemy.orm import Session


def test_create_user_duplicate_email(db):
    """Test creation of a user with a duplicate email."""
    user = UserCreate(
        email="testduplicateuser@example.com",
        password="password123",
        name="TestDuplicate",
    )
    create_user(db, user)

    with pytest.raises(UserExistsError):
        create_user(db, user)


def test_create_user(db):
    """Test user creation and verify user is stored correctly."""
    user = UserCreate(
        email="pedro@pandobando.com",
        password="password123",
        name="Pedro",
    )
    db_user = create_user(db, user)
    assert db_user.email == "pedro@pandobando.com"
    assert db_user.name == "Pedro"
    assert db_user.hashed_password is not None
    assert len(get_user(db)) == 1


def test_get_user_by_email(items, db):
    """Test retrieval of user by email."""
    user = get_user_by_email(db, "waldo@parillo.com")
    assert user is not None
    assert user.email == "waldo@parillo.com"


def test_get_user_by_id(items, db):
    """Test retrieval of user by ID."""
    user = get_user_by_id(db, 2)
    assert user is not None
    assert user.email == "waldo@parillo.com"
    assert user.id == 2


def test_delete_user(items, db):
    """Test deletion of user and verify user is removed."""
    user = get_user_by_id(db, 2)
    delete_user(db, user.id)
    user = get_user_by_id(db, 2)
    assert user is None

    with pytest.raises(UserNotFoundError):
        delete_user(db, 2)


def test_delete_user_not_found(db):
    """Test deletion of a user that does not exist."""
    with pytest.raises(UserNotFoundError):
        delete_user(db, user_id=99999)


def test_delete_user_error_handling(db, monkeypatch):
    """Test error handling during user deletion."""

    def mock_commit():
        raise exc.SQLAlchemyError("Mock commit error")

    user = UserCreate(
        email="testdeleteusererror@example.com",
        password="password123",
        name="TestDelete",
    )
    db_user = create_user(db, user)
    monkeypatch.setattr(db, "commit", mock_commit)

    with pytest.raises(UserNotDeletedError):
        delete_user(db, db_user.id)


def test_update_user_success(db, items):
    """Test successful update of a user."""

    # Update user details
    updated_user = UserUpdate(name="Quaddrazzo", email="quad@example.com")
    result = update_user(db, updated_user, 2)

    result = get_user_by_id(db, 2)

    assert result.name == "Quaddrazzo"
    assert result.email == "quad@example.com"


def test_update_user_not_found(db):
    """Test update of a user that does not exist."""
    updated_user = UserUpdate(name="NonexistentUser", email="updated@example.com")
    with pytest.raises(UserNotFoundError):
        update_user(db, updated_user, user_id=99999)


def test_update_user_error_handling(db, items, monkeypatch):
    """Test error handling during user update."""

    def mock_commit():
        raise exc.SQLAlchemyError("Mock commit error")

    monkeypatch.setattr(db, "commit", mock_commit)

    updated_user = UserUpdate(
        name="valid_name",
        email="valida@email.de",
    )
    with pytest.raises(UserNotUpdatedError):
        update_user(db, updated_user, 2)
