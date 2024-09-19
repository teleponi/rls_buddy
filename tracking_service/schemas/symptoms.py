from pydantic import BaseModel, ConfigDict, PositiveInt


class SymptomBase(BaseModel):
    name: str


class SymptomCreate(SymptomBase):
    pass


class Symptom(SymptomBase):  # todo rename to SymptomOut everywhere in code
    id: int


class SymptomOut(SymptomBase):
    id: int
