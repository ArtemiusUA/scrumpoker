import time
from pydantic import BaseModel


class Room(BaseModel):
    """Main app model to represent the room state."""

    id: str
    participants: dict = {}
    is_exposed: bool = False
    moderator: str = ""

    @staticmethod
    def generate_id():
        """Pseudo unique short value"""
        return str(int(round(time.time(), 2) * 100))[-6:]
