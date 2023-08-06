from typing import Any


class Err(Exception):
    def __init__(self, detail: Any, code: int = 400) -> None:
        self.code = code
        self.detail = detail
