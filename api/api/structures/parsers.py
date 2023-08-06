from __future__ import annotations

import functools
from enum import Enum
from typing import TYPE_CHECKING, Any, Type

if TYPE_CHECKING:
    from .objects import BSO, T


def _parse_to_flag(f: Any, val: int) -> Any:
    return f(val)


def _parse_id_to_object(obj: Type[BSO], val: int) -> T:
    return obj.from_id(val)


def _parse_to_object(obj: Type[BSO], val: Any) -> T:
    return obj.load(val)


def parse_to_flag(f: Enum):
    return functools.partial(_parse_to_flag, f)


def parse_to_int(val: Any) -> int:
    return int(val)


def parse_to_str(val: Any) -> str:
    return str(val)


def parse_to_object(obj: Any) -> Any:
    return functools.partial(_parse_to_object, obj)


def parse_id_to_object(obj: Any) -> Any:
    return functools.partial(_parse_id_to_object, obj)
