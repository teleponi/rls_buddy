"""
https://dev.to/jbrocher/fastapi-testing-a-database-5ao5
"""

import models
import schemes
from authentication import get_password_hash
from enums import Role

# from fastapi import HTTPException
# # from fastapi.security import OAuth2PasswordBearer
# from passlib.context import CryptContext
from sqlalchemy import exc, select
from sqlalchemy.orm import Session


class UserNotDeletedError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class UserNotValidError(Exception):
    pass


class UserNotUpdatedError(Exception):
    pass


class UserNotAllowedError(Exception):
    pass


class UserExistsError(Exception):
    pass


def get_user_by_email(db: Session, email: str) -> schemes.UserOut:
    items = select(models.User).where(models.User.email == email)
    return db.execute(items).scalars().first()


def get_user_by_id(db: Session, user_id: int) -> schemes.UserOut:
    items = select(models.User).where(models.User.id == user_id)
    return db.execute(items).scalars().first()


def get_user(db: Session) -> list[schemes.UserOut]:
    items = select(models.User)
    return db.execute(items).scalars().all()


def delete_user(db: Session, user_id: int) -> None:
    try:
        # Fetch the user instance to ensure it exists
        user = db.query(models.User).filter(models.User.id == user_id).one_or_none()
        if user is None:
            raise UserNotFoundError(f"User with id {user_id} does not exist.")

        db.delete(user)
        db.commit()
    except exc.SQLAlchemyError as e:
        raise UserNotDeletedError(f"User could not be deleted: {str(e)}")


def update_user(
    db: Session,
    user: schemes.UserUpdate,
    user_id: int,
) -> schemes.UserOut:
    """Update an user entry in DB.

    Args:
        db (Session): DB session
        user (schemes.User): User data
        user_id (int): User ID

    Raises:
        UserNotFoundError: User not found
        UserNotDeletedError: User could not be deleted

    Returns:
        schemes.User: User data
    """
    try:
        db_user = db.query(models.User).filter(models.User.id == user_id).one_or_none()
        if db_user is None:
            raise UserNotFoundError(f"User with id {user_id} does not exist.")

        user_data = user.model_dump(exclude_unset=True)  # todo exclude_unset?
        for key, value in user_data.items():
            setattr(db_user, key, value)

        db.commit()
        db.refresh(db_user)
    except exc.SQLAlchemyError as e:
        raise UserNotUpdatedError(f"User could not be updated: {str(e)}")


def create_user(
    db: Session,
    user: schemes.UserCreate,
    role: Role = Role.USER,
) -> schemes.UserOut:
    """Create a user entry in DB.

    Args:
        db (Session): DB session
        user (schemes.UserCreate): User data
        role (Role): User role

    Raises:
        UserExistsError: Email already registered
        UserNotValidError: User is not valid

    Returns:
        schemes.User: User data
    """
    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if db_user:
        raise UserExistsError(
            "Email already registered",
        )

    hashed_password = get_password_hash(user.password)
    try:
        db_user = models.User(
            email=user.email,
            hashed_password=hashed_password,
            name=user.name,
            role=role,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        raise UserNotValidError(f"{str(e)}")
    return db_user
