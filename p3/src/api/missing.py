#
# SPDX: CPAL-1.0
#
# Copyright 2021-2023 Derailed. All rights reserved.
#

from enum import Enum
from typing import Literal, TypeVar, Union

from typing_extensions import Literal

T = TypeVar("T")


class Missing(Enum):
    MISSING = None

    def __bool__(self) -> Literal[False]:
        return False


MISSING: Literal[Missing.MISSING] = Missing.MISSING


Maybe = Union[T, Missing]
