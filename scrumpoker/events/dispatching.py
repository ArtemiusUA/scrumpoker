from collections import defaultdict
from typing import Callable

from scrumpoker.models import events, rooms
from scrumpoker.events import consts
from scrumpoker import redis

registry = defaultdict(list)


def register(event_type: str):
    """Event system decorator to register handler functions for specified event types."""

    def decorator(handler: Callable):
        registry[event_type].append(handler)
        return handler

    return decorator


def moderator_only(handler: Callable):
    """Permissions decorator to mark handler as available only for moderator."""
    handler.moderator_only = True
    return handler


async def moderator_check(event: events.Event):
    """Checking if we need moderator limitation for event."""
    session_id = event.data.get("session_id")
    room_id = event.data.get("room_id")
    if not session_id or not room_id:
        return False
    r = rooms.Room(id=room_id)
    await redis.read_model(r)
    return r.moderator == session_id


async def dispatch(event: events.Event):
    """Dispatching events to registered handlers based on events types."""
    results = []
    for func in registry[event.type]:
        if getattr(func, "moderator_only", False) and not await moderator_check(
            event
        ):
            results.append(
                events.Event(
                    type=consts.WSOut.PERMISSIONS_ERROR,
                    data={"description": "Awailable only for moderator"},
                )
            )
            continue
        result = await func(event.data)
        if result:
            results.append(result)
    return results
