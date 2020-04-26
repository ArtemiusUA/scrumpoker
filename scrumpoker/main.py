import asyncio

import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from scrumpoker import redis
from scrumpoker.conf import base_dir, settings
from scrumpoker.endpoints import index, room, ws
from scrumpoker.middleware import SessionIDMiddleware

routes = [Mount("/static", StaticFiles(directory=base_dir.joinpath("static")), name="static")]
routes.extend(index.routes)
routes.extend(room.routes)
routes.extend(ws.routes)

middleware = [
    Middleware(SessionMiddleware, secret_key=settings.secret_key),
    Middleware(SessionIDMiddleware),
]

app = Starlette(
    debug=settings.debug,
    routes=routes,
    middleware=middleware,
    on_startup=[lambda: asyncio.create_task(redis.listen())],
)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
