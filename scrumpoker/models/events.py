from pydantic import BaseModel


class Event(BaseModel):
    """Event model to transmit over the app events system"""

    type: str
    data: dict = {}
