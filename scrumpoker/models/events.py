from pydantic import BaseModel


class Event(BaseModel):
    type: str
    connections: dict = {}
    data: dict = {}
