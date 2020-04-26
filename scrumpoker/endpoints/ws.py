import logging
from collections import defaultdict

from starlette.routing import WebSocketRoute
from starlette.websockets import WebSocket, WebSocketState

from scrumpoker.events import dispatch
from scrumpoker.models.events import Event

logger = logging.getLogger(__name__)

connections = defaultdict(list)


async def ws(socket: WebSocket):
    room_id = socket.path_params.get("room_id")
    await socket.accept()
    connections[room_id].append(socket)
    session_id = socket.session.get("session_id")
    await dispatch(
        Event(type="connect", data=dict(room_id=room_id, session_id=session_id))
    )
    try:
        while True:
            if socket.client_state == WebSocketState.CONNECTED:
                payload = await socket.receive_json()
                event = Event(**payload)
                event.data["room_id"] = room_id
                event.data["session_id"] = session_id
                results = await dispatch(event)
                for result in results:
                    await socket.send_json(result)
    except Exception as e:
        logger.debug(f"Exception on socket interaction: {e}")
    finally:
        connections[room_id].remove(socket)
        await dispatch(
            Event(type="disconnect", data=dict(room_id=room_id, session_id=session_id))
        )


routes = [
    WebSocketRoute("/ws/{room_id}", ws),
]
