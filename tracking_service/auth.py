"""
Authentication Module for Tracking Service

This module is responsible for handling authentication and authorization
within the Tracking Microservice. It uses JWT tokens to validate user
identity and permissions by forwarding requests to the User Microservice
for token verification.

Key Components:
- OAuth2PasswordBearer: Manages the extraction of Bearer tokens from
  incoming requests for authorization.
- JWT Token Validation: The user's token is forwarded to the User Service
  for validation, and the user ID is returned if the token is valid.
- Error Handling: Appropriate HTTP exceptions are raised if the token
  is invalid, unauthorized, or if any other issue occurs during the
  validation process.

This module ensures that the correct user context is enforced when
performing actions on the tracking data by requiring a valid token
with the necessary security scopes.

Author: Bernd Fischer, 2024
"""

import os
import sys

import httpx
import jwt
import schemas as schemes
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from loguru import logger


SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = 30

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",  # nur für die Dokumentation
)

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8001")
logger.add(sys.stderr, format="{level} {time} {message}", colorize=True, level="INFO")


# def verify_token(
#     security_scopes: SecurityScopes,
#     token: str = Depends(oauth2_scheme),
# ) -> int:
#     """Verifies the token and returns the user ID."""
#
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id: str = payload.get("sub")
#         if user_id is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
#         token_scopes = payload.get("scopes", [])
#         token_data = schemes.basic.TokenData(scopes=token_scopes, user_id=user_id)
#
#     except jwt.PyJWTError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Could not validate credentials",
#         )
#
#     # as defined in the OAuth2PasswordBearer
#     for scope in security_scopes.scopes:
#         if scope not in token_data.scopes:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Not enough permissions",
#             )
#
#     return int(user_id)
#


async def get_user_id_from_token(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
) -> int:
    """Forward the token to the user service and get the user ID if valid."""

    headers = {"Authorization": f"Bearer {token}"}
    s = ",".join(security_scopes.scopes)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{USER_SERVICE_URL}/token-validate?scopes={s}",
            headers=headers,
        )
        if response.status_code == status.HTTP_200_OK:
            try:
                return int(response.json().get("user_id"))
            except (ValueError, TypeError) as e:
                logger.error(f"User ipdb_id not found in token: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="User ID not found in token!",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
