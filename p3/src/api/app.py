# Copyright (C) 2021-2023 Derailed
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
from typing import Any, Callable

import dotenv
import msgspec
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from models.error import Err
from tortoise import Tortoise


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
    title="Derailed API",
    description="OpenAPI documentation of the Derailed API",
    version="0.1.0",
    default_response_class=MSGSpecResponse,
)
app.router.route_class = MSGSpecRoute


@app.exception_handler(Err)
def custom_error(request: Request, exc: Err):
    return MSGSpecResponse({"detail": exc.detail}, status_code=exc.code)


@app.on_event("startup")
async def on_startup() -> None:
    dotenv.load_dotenv()

    await Tortoise.init(db_url=os.environ["DB_URL"], modules={"models": ["models"]})
    await Tortoise.generate_schemas()
