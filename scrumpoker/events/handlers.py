import logging

from scrumpoker import redis
from scrumpoker.endpoints.ws import connections
from scrumpoker.events.consts import Redis, WSIn, WSOut
from scrumpoker.events.dispatching import moderator_only, register
from scrumpoker.models import Event, Room

logger = logging.getLogger(__name__)


@register(WSIn.CONNECT)
async def on_connect(data: dict):
    """
    Event handler for new websocket connection.

    Adding user to room participants if not added yet
    and publishing notification to Redis on room update
    """
    logger.info(f"Connected: {data}")
    room_id = data.get("room_id")
    session_id = data.get("session_id")
    r = Room(id=room_id)
    await redis.read_model(r)
    if session_id and session_id not in r.participants:
        r.participants[session_id] = False
        await redis.save_model(r)
        await redis.notify_model_changed(r)
    return Event(type=WSOut.ROOM_UPDATE, data=r.dict())


@register(WSIn.DISCONNECT)
async def on_disconnect(data: dict):
    """
    Event handler for closed websocket connection.

    Removing user from room participants
    and publishing notification to Redis on room update
    """
    logger.info(f"Disconnected: {data}")
    room_id = data.get("room_id")
    session_id = data.get("session_id")
    r = Room(id=room_id)
    await redis.read_model(r)
    r.participants.pop(session_id, None)
    await redis.save_model(r)
    await redis.notify_model_changed(r)


@register(WSIn.RESET)
@moderator_only
async def on_reset(data: dict):
    """Reseting participants votes in room."""
    logger.info(f"Reset: {data}")
    room_id = data.get("room_id")
    r = Room(id=room_id)
    await redis.read_model(r)
    r.is_exposed = False
    r.participants = {k: None for k in r.participants}
    await redis.save_model(r)
    await redis.notify_model_changed(r)


@register(WSIn.VOTE)
async def on_vote(data: dict):
    """Registering vote sent by participant."""
    logger.info(f"Vote: {data}")
    room_id = data.get("room_id")
    session_id = data.get("session_id")
    points = data.get("points")
    r = Room(id=room_id)
    await redis.read_model(r)
    r.participants[session_id] = points
    await redis.save_model(r)
    await redis.notify_model_changed(r)


@register(WSIn.EXPOSE)
@moderator_only
async def on_expose(data: dict):
    """
    Exposing votes of participants that normally
    are not visible to all till moderator decision.
    """
    logger.info(f"Expose: {data}")
    room_id = data.get("room_id")
    session_id = data.get("session_id")
    r = Room(id=room_id)
    await redis.read_model(r)
    r.is_exposed = True
    await redis.save_model(r)
    await redis.notify_model_changed(r)


@register(Redis.MODEL_CHANGE)
async def on_model_change(data: dict):
    """Updating connected users on room change event received from Redis pub/sup."""
    logger.info(f"model_change: {data}")
    if data.get("model") != Room.__name__:
        return
    r = Room(id=data.get("id"))
    await redis.read_model(r)
    room_connections = connections.get(r.id)
    for c in room_connections:
        # copy of the state with exposed point for owner
        state = r.copy()
        if not r.is_exposed:
            state.participants = {
                k: v
                if k == c.session.get("session_id") and v is not None
                else bool(v)
                for k, v in r.participants.items()
            }
        else:
            state.participants = {
                k: v if v is not None else bool(v)
                for k, v in r.participants.items()
            }
        await c.send_json(
            Event(type=WSOut.ROOM_UPDATE, data=state.dict()).dict()
        )
