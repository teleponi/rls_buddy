from datetime import timedelta
from typing import Annotated

import authentication
import crud
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm, SecurityScopes
from schemes import Token
from sqlalchemy.orm import Session


router = APIRouter(tags=["Authentification"])


@router.get("/token-validate")
async def validate_token(
    request: Request,
    token: str = Depends(authentication.oauth2_scheme),
    db: Session = Depends(get_db),
) -> dict:
    """Validate and check for scopes in token."""
    scopes = request.query_params.get("scopes", "")
    security_scopes = SecurityScopes(scopes=scopes.split(","))
    db, user_id = authentication.verify_token(security_scopes, token, db)
    return {"user_id": user_id}


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> dict:
    """
    Get an access token

    -d '{"ail": "alice@example.com", "password": "secret"}'
    """
    user = crud.get_user_by_email(db, form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    authentication.verify(form_data.password, user.hashed_password)
    access_token_expires = timedelta(minutes=30)
    access_token = authentication.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}
