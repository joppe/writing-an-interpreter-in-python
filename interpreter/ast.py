from abc import ABC, abstractmethod

from interpreter.token import Token


class Node(ABC):
    @abstractmethod
    def token_literal(self) -> str:
        raise NotImplementedError


class Statement(Node):
    def __init__(self, token: Token) -> None:
        self.token = token

    def __repr__(self) -> str:
        return self.token.literal

    def token_literal(self) -> str:
        return self.token.literal


class Expression(Node):
    def __init__(self, token: Token) -> None:
        self.token = token

    def __repr__(self) -> str:
        return self.token.literal

    def token_literal(self) -> str:
        return self.token.literal


class Program(Node):
    def __init__(self, statements: list[Statement] = []) -> None:
        self.statements = statements

    def __repr__(self) -> str:
        return "".join([str(statement) for statement in self.statements])

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


class ReturnStatement(Statement):
    def __init__(self, token: Token, return_value: Expression) -> None:
        super().__init__(token)

        self.return_value = return_value
