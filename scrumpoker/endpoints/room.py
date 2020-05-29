import random

from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.routing import Route

from scrumpoker import redis
from scrumpoker.conf import templates
from scrumpoker.models.rooms import Room


async def create_room(request: Request):
    room_id = random.randint(10000, 99999)
    await redis.save_model(Room(id=room_id, moderator=request.session.get("session_id")))
    return RedirectResponse(f"/room/{room_id}", status_code=302)


async def view_room(request: Request):
    room = await redis.read_model(Room(id=request.path_params.get("room_id")))
    return templates.TemplateResponse("room.html", {"request": request, "room": room})


routes = [
    Route("/room", create_room, methods=["POST"]),
    Route("/room/{room_id}", view_room),
]
