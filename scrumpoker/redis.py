import json

import aioredis
from pydantic import BaseModel

from scrumpoker.conf import settings
from scrumpoker.events import dispatch
from scrumpoker.models.events import Event

_rc = None
_ch = None


async def get_connection():
    global _rc
    if _rc is None:
        _rc = await aioredis.create_redis_pool(settings.redis_url)
    return _rc


async def get_channel():
    global _ch
    if _ch is None:
        conn = await aioredis.create_redis(settings.redis_url)
        results = await conn.psubscribe("model_change:*")
        _ch = results[0]
    return _ch


async def save_model(instance: BaseModel):
    rc = await get_connection()
    await rc.set(f"{instance.__class__.__name__}:{instance.id}", instance.json())


async def read_model(instance: BaseModel):
    rc = await get_connection()
    data = await rc.get(f"{instance.__class__.__name__}:{instance.id}")
    try:
        return instance.copy(update=json.loads(data))
    except Exception:
        return instance


async def notify_model_changed(instance: BaseModel):
    rc = await get_connection()
    await rc.publish(f"model_change:{instance.__class__.__name__}", instance.json())


async def listen():
    ch = await get_channel()
    while await ch.wait_message():
        channel, data = await ch.get_json()
        event = Event(type=channel.decode(), data=data)
        await dispatch(event)

