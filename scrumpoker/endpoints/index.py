from starlette.requests import Request
from starlette.routing import Route

from scrumpoker.conf import settings, templates


async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


routes = [Route("/", index, methods=["get"])]
