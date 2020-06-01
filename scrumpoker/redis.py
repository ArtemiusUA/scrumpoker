import logging

import aioredis
from pydantic import BaseModel

from scrumpoker.conf import settings
from scrumpoker.events import consts, dispatch
from scrumpoker.models.events import Event

logger = logging.getLogger(__name__)
_rc = None
_listener = None
_ch = None


async def get_connection():
    """
    Creating and accessing the main Redis connections pool singleton.

    :return: connection pull
    """
    global _rc
    if _rc is None:
        _rc = await aioredis.create_redis_pool(settings.redis_url)
    return _rc


async def close_connection():
    """Closing main Redis connections pool"""
    global _rc
    if _rc is not None:
        await _rc.close()


async def get_listener():
    """
    Creating and accessing Redis listener connection used for pub/sub mode.

    :return: listener connection
    """
    global _listener
    if _listener is None:
        _listener = await aioredis.create_redis(settings.redis_url)
    return _listener


async def close_listener():
    """Closing Redis listener connection"""
    global _listener
    if _listener is not None:
        await _listener.close()


async def get_channel():
    """
    Subscribing and accessing the main notifications chanel.

    :return: model_change channel
    """
    global _ch
    if _ch is None:
        conn = await get_listener()
        results = await conn.subscribe("model_change")
        _ch = results[0]
    return _ch


async def save_model(instance: BaseModel):
    """Saving model to Redis."""
    rc = await get_connection()
    await rc.set(
        f"{instance.__class__.__name__}:{instance.id}",
        instance.json(),
        expire=settings.model_ttl,
    )


async def read_model(instance: BaseModel):
    """
    Reading model from Redis by id attribute from model.

    :return: instance
    """
    rc = await get_connection()
    data = await rc.get(f"{instance.__class__.__name__}:{instance.id}")
    try:
        for k, v in instance.__class__.parse_raw(data).dict().items():
            setattr(instance, k, v)
    except Exception as e:
        logger.exception(f"Unable to load model: {e}")


async def notify_model_changed(instance: BaseModel):
    """Publishing event to Redis channel."""
    rc = await get_connection()
    await rc.publish(
        consts.Redis.MODEL_CHANGE,
        Event(
            type=consts.Redis.MODEL_CHANGE,
            data={"model": instance.__class__.__name__, "id": instance.id},
        ).json(),
    )


async def listen():
    """
    Infinite listener coroutine to get events from
    Redis channel and promote them to handlers.
    """
    ch = await get_channel()
    while await ch.wait_message():
        data = await ch.get_json()
        event = Event(**data)
        await dispatch(event)
