import logging
from collections import defaultdict, namedtuple

from pydantic import ValidationError
from starlette.endpoints import WebSocketEndpoint
from starlette.routing import WebSocketRoute
from starlette.websockets import WebSocket

from scrumpoker.events import dispatch
from scrumpoker.models.events import Event

logger = logging.getLogger(__name__)

connections = defaultdict(list)
Idents = namedtuple("Identities", "room_id session_id")


class WS(WebSocketEndpoint):
    encoding = "json"

    @staticmethod
    def get_idents(websocket: WebSocket) -> Idents:
        return Idents(
            websocket.path_params.get("room_id"), websocket.session.get("session_id")
        )

    async def on_connect(self, websocket: WebSocket) -> None:
        await super().on_connect(websocket)
        ident = self.get_idents(websocket)
        connections[ident.room_id].append(websocket)
        await dispatch(
            Event(
                type="connect",
                data=dict(room_id=ident.room_id, session_id=ident.session_id),
            )
        )

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        idents = self.get_idents(websocket)
        connections[idents.room_id].remove(websocket)
        await dispatch(
            Event(
                type="disconnect",
                data=dict(room_id=idents.room_id, session_id=idents.session_id),
            )
        )

    async def on_receive(self, websocket: WebSocket, data: dict) -> None:
        idents = self.get_idents(websocket)
        try:
            event = Event(**data)
        except ValidationError as e:
            await websocket.send_json(
                Event(type="validation_error", data={"info": str(e)}).dict()
            )
            return
        event.data["room_id"] = idents.room_id
        event.data["session_id"] = idents.session_id
        results = await dispatch(event)
        for result in results:
            await websocket.send_json(result)


routes = [
    WebSocketRoute("/ws/{room_id}", WS),
]
