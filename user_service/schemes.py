import re

from enums import Role
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    ValidationError,
    constr,
    field_validator,
)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int | None = None
    scopes: list[str] = []


class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    role: Role | None = None


class UserAuth(BaseModel):
    email: EmailStr
    password: constr(min_length=4)
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "alice@example.com",
                "password": "secret",
            }
        }
    )


class UserUpdate(BaseModel):
    email: EmailStr
    name: constr(min_length=2)

    @field_validator("name")
    @classmethod
    def ensure_valid_name(cls, value):
        allowed_characters = re.compile(r"^[a-zA-Z0-9öäüÖÄÜ_]*$")
        if " " in value:
            raise ValueError("Spaces are not allowed in the name")

        if not allowed_characters.match(value):
            raise ValueError("Name contains invalid characters.")

        return value

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Grumpy Cat",
                "email": "grumpy@cat.com",
                "password": "weakpassword",
            }
        }
    )


class UserCreate(UserUpdate):
    password: constr(min_length=4)
