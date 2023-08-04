from typing import Any, TypedDict


class GuildMetadata(TypedDict):
    presences: int
    available: bool


# TODO: add gRPC
class RPCController:
    def __init__(self) -> None:
        ...

    async def publish_guild(self, guild_id: int, type: str, data: Any) -> None:
        ...

    async def publish_user(self, user_id: int, type: str, data: Any) -> None:
        ...

    async def multipublish(self, user_ids: list[int], type: str, data: Any) -> None:
        ...

    async def get_activity(self, guild_id: int) -> GuildMetadata:
        ...


rpc = RPCController()


async def publish_guild(guild_id: int, type: str, data: Any) -> None:
    await rpc.publish_guild(guild_id, type, data)


async def publish_user(user_id: int, type: str, data: Any) -> None:
    await rpc.publish_user(user_id, type, data)


async def multipublish(user_ids: list[int], type: str, data: Any) -> None:
    await rpc.multipublish(user_ids, type, data)


async def get_activity(guild_id: int) -> GuildMetadata:
    return await rpc.get_activity(guild_id)
