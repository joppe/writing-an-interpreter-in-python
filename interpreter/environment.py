from __future__ import annotations
from typing import Dict, Optional

from interpreter import object


class Environment:
    def __init__(self, outer: Optional[Environment] = None) -> None:
        self.store: Dict[str, object.Object] = {}
        self.outer = outer

    def get(self, name: str) -> object.Object | None:
        if name not in self.store:
            if self.outer is not None:
                return self.outer.get(name)

            return None

        return self.store[name]

    def set(self, name: str, value: object.Object) -> object.Object:
        self.store[name] = value

        return value

    @staticmethod
    def new_environment() -> Environment:
        env = Environment()

        return env

    @staticmethod
    def new_enclosed_environment(outer: Environment) -> Environment:
        env = Environment(outer)

        return env
