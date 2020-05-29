from pydantic import BaseModel


class Event(BaseModel):
    type: str
    data: dict = {}
