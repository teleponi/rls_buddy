from enums import TriggerCategory
from pydantic import BaseModel


class TriggerBase(BaseModel):
    name: str
    category: TriggerCategory


class TriggerCreate(TriggerBase):
    pass


class TriggerOut(TriggerBase):
    id: int
