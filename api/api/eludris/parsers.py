from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .objects import T


def parse_to_flag(f: T, val: int) -> T:
    return f(val)
