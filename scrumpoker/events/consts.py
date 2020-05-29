class WSIn:
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    RESET = "reset"
    VOTE = "vote"
    EXPOSE = "expose"


class WSOut:
    ROOM_UPDATE = "room_update"
    VALIDATION_ERROR = "validation_error"


class Redis:
    MODEL_CHANGE = "model_change"
