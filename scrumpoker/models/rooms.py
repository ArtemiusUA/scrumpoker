from pydantic import BaseModel


class Room(BaseModel):
    id: str
    participants: dict = {}
