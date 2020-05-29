from pydantic import BaseModel


class Room(BaseModel):
    id: str
    participants: dict = {}
    is_exposed: bool = False
    moderator: str = ""

