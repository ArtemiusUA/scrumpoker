import random

from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.routing import Route

from scrumpoker import redis
from scrumpoker.conf import templates, votes_sequence
from scrumpoker.models.rooms import Room


async def create_room(request: Request):
    room_id = Room.generate_id()
    await redis.save_model(
        Room(
            id=room_id,
            moderator=request.session.get("session_id"),
            votes_sequence=votes_sequence,
        )
    )
    return RedirectResponse(f"/room/{room_id}", status_code=302)


async def view_room(request: Request):
    r = Room(id=request.path_params.get("room_id"))
    await redis.read_model(r)
    session_id = request.session.get("session_id")
    return templates.TemplateResponse(
        "room.html", {"request": request, "room": r, "is_moderator": session_id == r.moderator},
    )


routes = [
    Route("/room", create_room, methods=["POST"]),
    Route("/room/{room_id}", view_room),
]
