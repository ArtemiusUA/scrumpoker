from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware


class SessionIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if not request.session.get("session_id"):
            request.session["session_id"] = str(uuid4())
        response = await call_next(request)
        return response
