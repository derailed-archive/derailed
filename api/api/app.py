from typing import Any, Callable, TypedDict, final

import msgspec
from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from .controllers.rate_limiter import UnscopedRateLimiter
from .error import Err


class MSGSpecResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return msgspec.json.encode(content)


class MSGSpecRequest(Request):
    async def json(self) -> Any:
        if not hasattr(self, "_json"):
            body = await self.body()
            self._json = msgspec.json.decode(body)
        return self._json


class MSGSpecRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            request = MSGSpecRequest(request.scope, request.receive)
            return await original_route_handler(request)

        return custom_route_handler


app = FastAPI(
    default_response_class=MSGSpecResponse,
    dependencies=[Depends(UnscopedRateLimiter("global", 80, 60, True))],
)
app.router.route_class = MSGSpecRoute


@final
class Exc(TypedDict):
    detail: Any


@app.exception_handler(Err)
async def exception(request: Request, exc: Err) -> Exc:
    return MSGSpecResponse({"detail": exc.detail}, exc.code)
