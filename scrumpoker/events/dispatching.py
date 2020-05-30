from collections import defaultdict
from typing import Callable

from scrumpoker.models import events

registry = defaultdict(list)


def register(event_type: str):
    """Event system decorator to register handler functions for specified event types."""

    def decorator(handler: Callable):
        registry[event_type].append(handler)
        return handler

    return decorator


async def dispatch(event: events.Event):
    """Dispatching events to registered handlers based on events types."""
    results = []
    for func in registry[event.type]:
        result = await func(event.data)
        if result:
            results.append(result)
    return results
