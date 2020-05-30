from pydantic import BaseModel


class Room(BaseModel):
    """Main app model to represent the room state."""

    id: str
    participants: dict = {}
    is_exposed: bool = False
    moderator: str = ""
