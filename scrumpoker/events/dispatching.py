from collections import defaultdict
from typing import Callable

from scrumpoker.models import events

registry = defaultdict(list)


def register(event_type: str):
    def decorator(handler: Callable):
        registry[event_type].append(handler)
        return handler

    return decorator


async def dispatch(event: events.Event):
    results = []
    for func in registry[event.type]:
        result = await func(event.data)
        if result:
            results.append(result)
    return results
