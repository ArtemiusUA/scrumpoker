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


def create_routes():
    routes = [
        Mount(
            "/static",
            StaticFiles(directory=base_dir.joinpath("static")),
            name="static",
        )
    ]
    routes.extend(index.routes)
    routes.extend(room.routes)
    routes.extend(ws.routes)
    return routes


def create_middleware():
    middleware = list()
    middleware.append(
        Middleware(SessionMiddleware, secret_key=settings.secret_key)
    )
    middleware.append(Middleware(SessionIDMiddleware))
    return middleware


def create_startup_actions():
    actions = list()
    actions.append(lambda: asyncio.create_task(redis.listen()))
    return actions


def create_shutdown_actions():
    actions = list()
    actions.append(redis.close_connection)
    actions.append(redis.close_listener)
    return actions


def create_app():
    app = Starlette(
        debug=settings.debug,
        routes=create_routes(),
        middleware=create_middleware(),
        on_startup=create_startup_actions(),
        on_shutdown=create_shutdown_actions(),
    )
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
