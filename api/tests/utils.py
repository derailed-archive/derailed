from contextvars import ContextVar

import anyio

token_context: ContextVar[str] = ContextVar("token", default="")


def set_token(token: str) -> None:
    token_context.set(token)


async def wait_for_token() -> None:
    while True:
        t = token_context.get()

        if t == "":
            await anyio.sleep(1)
        else:
            break
