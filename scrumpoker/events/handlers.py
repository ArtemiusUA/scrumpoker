import logging

from scrumpoker import redis
from scrumpoker.endpoints.ws import connections
from scrumpoker.models import Event, Room

from . import register
from .consts import Redis, WSIn, WSOut

logger = logging.getLogger(__name__)


@register(WSIn.CONNECT)
async def on_connect(data: dict):
    logger.info(f"Connected: {data}")
    room_id = data.get("room_id")
    session_id = data.get("session_id")
    r = await redis.read_model(Room(id=room_id))
    if session_id and session_id not in r.participants:
        r.participants[session_id] = None
        await redis.save_model(r)
        await redis.notify_model_changed(r)


@register(WSIn.DISCONNECT)
async def on_disconnect(data: dict):
    logger.info(f"Disconnected: {data}")
    room_id = data.get("room_id")
    session_id = data.get("session_id")
    r = await redis.read_model(Room(id=room_id))
    r.participants.pop(session_id, None)
    await redis.notify_model_changed(r)


@register(WSIn.RESET)
async def on_reset(data: dict):
    logger.info(f"Reset: {data}")


@register(WSIn.VOTE)
async def on_vote(data: dict):
    logger.info(f"Vote: {data}")


@register(WSIn.EXPOSE)
async def on_expose(data: dict):
    logger.info(f"Expose: {data}")


@register(Redis.MODEL_CHANGE)
async def on_model_change(data: dict):
    logger.info(f"model_change: {data}")
    if data.get("model") != Room.__name__:
        return
    r = await redis.read_model(Room(id=data.get("id")))
    room_connections = connections.get(r.id)
    for c in room_connections:
        await c.send_json(Event(type=WSOut.ROOM_UPDATE, data=r.dict()).dict())
