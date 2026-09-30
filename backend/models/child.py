from pydantic import BaseModel
from datetime import date


class ChildCreate(BaseModel):
    name: str
    date_of_birth: date
    gender: str
    centre: str