import authentication
import crud
from authentication import get_current_user
from database import get_db
from enums import Role
from events import publish_user_delete_event
from fastapi import APIRouter, Depends, HTTPException, Security, status
from loguru import logger
from schemes import UserCreate, UserOut, UserUpdate
from sqlalchemy.orm import Session


router = APIRouter(prefix="/users", tags=["User"])


@router.get("/me", response_model=UserOut)
def read_users_me(
    current_user: UserOut = Security(get_current_user, scopes=["me"])
) -> UserOut:
    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id_db: tuple[Session, int] = Security(
        authentication.verify_token, scopes=["me"]
    ),
    # current_user_id: UserOut = Security(authentication.verify_token, scopes=["me"]),
    # db: Session = Depends(get_db),
) -> None:
    """
    Delete authenticated user

    curl -X DELETE "http://localhost:8000/users/me/delete"

    Raises:
        HTTPException: User not found

    Returns:
        None
    """
    db, current_user_id = user_id_db
    try:
        crud.delete_user(db, current_user_id)
    except crud.UserNotDeletedError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User could not be deleted." + str(e),
        )
    event = {"type": "USER_DELETED", "user_id": current_user_id}
    publish_user_delete_event(event)


@router.post("/admin", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_admin_user(
    user: UserCreate,
    user_id_db: tuple[Session, int] = Security(
        authentication.verify_token, scopes=["me"]
    ),
    # db: Session = Depends(get_db),
) -> UserOut:
    """
    Create a new admin user.
    """

    db, current_user_id = user_id_db
    logger.info(f" User {current_user_id} created a new user adminuser {user}")
    try:
        return crud.create_user(db, user, role=Role.ADMIN)
    except crud.UserExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists." + str(e),
        )


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
) -> UserOut:
    """
    Create a new standard user.
    """
    try:
        return crud.create_user(db, user, role=Role.USER)
    except crud.UserExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists.",
        )
    except crud.UserNotValidError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data is not valid." + str(e),
        )


@router.put("/", response_model=UserOut, status_code=status.HTTP_200_OK)
def update_user(
    user: UserUpdate,
    user_id_db: tuple[Session, int] = Security(
        authentication.verify_token, scopes=["me"]
    ),
) -> UserOut:
    """
    Create a new standard user.
    """
    db, current_user_id = user_id_db
    try:
        return crud.update_user(db, user, current_user_id)
    except crud.UserExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists." + str(e),
        )
    except crud.UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    except crud.UserNotAllowedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"{e}",
        )
