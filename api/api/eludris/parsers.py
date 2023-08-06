from __future__ import annotations

from typing import TYPE_CHECKING, Any, Type

if TYPE_CHECKING:
    from .objects import BSO, T


def parse_to_flag(f: T, val: int) -> T:
    return f(val)


def parse_id_to_object(obj: Type[BSO], val: int) -> T:
    return obj.from_id(val)


def parse_to_object(obj: Type[BSO], val: Any) -> T:
    return obj.load(val)


def parse_to_int(val: Any) -> int:
    return int(val)


def parse_to_str(val: Any) -> str:
    return str(val)
