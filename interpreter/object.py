from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, Dict

from interpreter import ast
from interpreter import environment


class ObjectType(Enum):
    INTEGER = "ILLEGAL"
    BOOLEAN = "BOOLEAN"
    NULL = "NULL"
    RETURN_VALUE = "RETURN_VALUE"
    ERROR = "ERROR"
    FUNCTION = "FUNCTION"
    STRING = "STRING"
    ARRAY = "ARRAY"
    HASH = "HASH"

    def __repr__(self) -> str:
        return self._name_


class HashKey:
    def __init__(self, type: ObjectType, value: int) -> None:
        self.type = type
        self.value = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HashKey):
            return False

        return self.type == other.type and self.value == other.value

    def __hash__(self) -> int:
        return hash((self.type, self.value))


class Hashable(ABC):
    @abstractmethod
    def hash_key(self) -> HashKey:
        raise NotImplementedError


class Object(ABC):
    @abstractmethod
    def type(self) -> ObjectType:
        raise NotImplementedError

    @abstractmethod
    def inspect(self) -> str:
        raise NotImplementedError


class Integer(Object, Hashable):
    def __init__(self, value: int) -> None:
        self.value = value

    def type(self) -> ObjectType:
        return ObjectType.INTEGER

    def inspect(self) -> str:
        return f"{self.value}"

    def hash_key(self) -> HashKey:
        return HashKey(self.type(), self.value)


class String(Object, Hashable):
    def __init__(self, value: str) -> None:
        self.value = value

    def type(self) -> ObjectType:
        return ObjectType.STRING

    def inspect(self) -> str:
        return self.value

    def hash_key(self) -> HashKey:
        return HashKey(self.type(), hash(self.value))


class Boolean(Object, Hashable):
    def __init__(self, value: bool) -> None:
        self.value = value

    def type(self) -> ObjectType:
        return ObjectType.BOOLEAN

    def inspect(self) -> str:
        return f"{self.value}"

    def hash_key(self) -> HashKey:
        value = 1 if self.value else 0

        return HashKey(self.type(), value)


class Null(Object):
    def type(self) -> ObjectType:
        return ObjectType.NULL

    def inspect(self) -> str:
        return "null"


class ReturnValue(Object):
    def __init__(self, value: Object) -> None:
        self.value = value

    def type(self) -> ObjectType:
        return ObjectType.RETURN_VALUE

    def inspect(self) -> str:
        return self.value.inspect()


class Error(Object):
    def __init__(self, message: str) -> None:
        self.message = message

    def type(self) -> ObjectType:
        return ObjectType.ERROR

    def inspect(self) -> str:
        return f"ERROR: {self.message}"


class Function(Object):
    def __init__(
        self,
        parameters: list[ast.Identifier],
        body: ast.BlockStatement,
        env: environment.Environment,
    ) -> None:
        self.parameters = parameters
        self.body = body
        self.env = env

    def type(self) -> ObjectType:
        return ObjectType.FUNCTION

    def inspect(self) -> str:
        return f"fn({', '.join([str(p) for p in self.parameters])}) {{\n{self.body}\n}}"


class Array(Object):
    def __init__(self, elements: list[Object]) -> None:
        self.elements = elements

    def type(self) -> ObjectType:
        return ObjectType.ARRAY

    def inspect(self) -> str:
        return f"[{', '.join([e.inspect() for e in self.elements])}]"


class Builtin(Object):
    def __init__(self, fn: Callable[[list[Object]], Object]) -> None:
        self.fn = fn

    def type(self) -> ObjectType:
        return ObjectType.FUNCTION

    def inspect(self) -> str:
        return "builtin function"


class HashPair:
    def __init__(self, key: Object, value: Object) -> None:
        self.key = key
        self.value = value

    def __repr__(self) -> str:
        return f"{self.key.inspect()}: {self.value.inspect()}"


class Hash(Object):
    def __init__(self, pairs: Dict[HashKey, HashPair]) -> None:
        self.pairs = pairs

    def type(self) -> ObjectType:
        return ObjectType.HASH

    def inspect(self) -> str:
        return f"{{{', '.join([f'{pair}' for _, pair in self.pairs.items()])}}}"
