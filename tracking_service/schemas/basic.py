from datetime import datetime

from pydantic import BaseModel, ConfigDict, PositiveInt


class TokenData(BaseModel):
    user_id: int | None = None
    scopes: list[str] = []


class TrackingCreate(BaseModel):
    model_config = ConfigDict(
        # extra="allow",
    )


class TrackingUpdate(BaseModel):
    pass


class TrackingOut(BaseModel):
    id: int
    user_id: int
    timestamp: datetime
