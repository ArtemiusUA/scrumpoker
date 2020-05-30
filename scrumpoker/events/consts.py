class WSIn:
    """Incoming websocket events types."""

    CONNECT = "connect"
    DISCONNECT = "disconnect"
    RESET = "reset"
    VOTE = "vote"
    EXPOSE = "expose"


class WSOut:
    """Outgoing websocket events types."""

    ROOM_UPDATE = "room_update"
    VALIDATION_ERROR = "validation_error"


class Redis:
    """Redis pub/sub events types."""

    MODEL_CHANGE = "model_change"
