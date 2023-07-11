#
# SPDX: CPAL-1.0
#
# Copyright 2021-2023 Derailed. All rights reserved.
#

from typing import Any


class Err(Exception):
    def __init__(self, detail: Any, code: int = 400) -> None:
        self.detail = detail
        self.code = code
