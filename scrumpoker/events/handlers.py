import logging

from scrumpoker import redis
from scrumpoker.endpoints.ws import connections
from scrumpoker.models.rooms import Room

from . import register

logger = logging.getLogger(__name__)


@register("connect")
async def on_connect(data):
    logger.info(f"Connected: {data}")
    room_id = data.get("room_id")
    session_id = data.get("session_id")
    r = await redis.read_model(Room(id=room_id))
    if session_id and session_id not in r.participants:
        r.participants[session_id] = None
        await redis.save_model(r)
        await redis.notify_model_changed(r)


@register("disconnect")
async def on_disconnect(data):
    logger.info(f"Disconnected: {data}")


@register("reset")
async def on_reset(data):
    logger.info(f"Reseted: {data}")


@register("vote")
async def on_vote(data):
    logger.info(f"Voted: {data}")


@register("exposed")
async def on_expose(data):
    logger.info(f"Exposed: {data}")


@register("model_change:Room")
async def on_room_change(data):
    logger.info(f"model_change:Room: {data}")
    r = await redis.read_model(Room(**data))
    room_connections = connections.get(r.id)
    for c in room_connections:
        await c.send_json({"type": "room_updated", "data": r.json()})
