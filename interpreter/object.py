from abc import ABC, abstractmethod
from enum import Enum

from interpreter import ast
from interpreter import environment


class ObjectType(Enum):
    INTEGER = "ILLEGAL"
    BOOLEAN = "BOOLEAN"
    NULL = "NULL"
    RETURN_VALUE = "RETURN_VALUE"
    ERROR = "ERROR"
    FUNCTION = "FUNCTION"

    def __repr__(self) -> str:
        return self._name_


class Object(ABC):
    @abstractmethod
    def type(self) -> ObjectType:
        raise NotImplementedError

    @abstractmethod
    def inspect(self) -> str:
        raise NotImplementedError


class Integer(Object):
    def __init__(self, value: int) -> None:
        self.value = value

    def type(self) -> ObjectType:
        return ObjectType.INTEGER

    def inspect(self) -> str:
        return f"{self.value}"


class Boolean(Object):
    def __init__(self, value: bool) -> None:
        self.value = value

    def type(self) -> ObjectType:
        return ObjectType.BOOLEAN

    def inspect(self) -> str:
        return f"{self.value}"


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
