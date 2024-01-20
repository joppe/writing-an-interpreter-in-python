from __future__ import annotations
from typing import Dict

from interpreter import object


class Environment:
    def __init__(self) -> None:
        self.store: Dict[str, object.Object] = {}

    def get(self, name: str) -> object.Object | None:
        if name not in self.store:
            return None

        return self.store[name]

    def set(self, name: str, value: object.Object) -> object.Object:
        self.store[name] = value

        return value

    @staticmethod
    def new_environment() -> Environment:
        env = Environment()

        return env
