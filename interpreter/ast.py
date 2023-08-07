from abc import ABC, abstractmethod

from interpreter.token import Token


class Node(ABC):
    @abstractmethod
    def token_literal(self) -> str:
        raise NotImplementedError


class Statement(Node):
    def __init__(self, token: Token):
        self.token = token

    def token_literal(self) -> str:
        return self.token.literal


class Expression(Node):
    def __init__(self, token: Token):
        self.token = token

    def token_literal(self) -> str:
        return self.token.literal


class Program(Node):
    def __init__(self, statements: list[Statement] = []):
        self.statements = statements

    def token_literal(self) -> str:
        if len(self.statements) > 0:
            return self.statements[0].token_literal()
        else:
            return ""


class Identifier(Expression):
    def __init__(self, token: Token, value: str) -> None:
        super().__init__(token)

        self.value = value


class LetStatement(Statement):
    def __init__(self, token: Token, name: Identifier, expression: Expression) -> None:
        super().__init__(token)

        self.name = name
        self.expression = expression
