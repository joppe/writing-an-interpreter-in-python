from abc import ABC, abstractmethod
from interpreter.token import Token


class Node(ABC):
    @abstractmethod
    def token_literal(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
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
        out = ""

        for statement in self.statements:
            out += f"{statement}"

        return out

    def token_literal(self) -> str:
        if len(self.statements) > 0:
            return self.statements[0].token_literal()
        else:
            return ""


class Identifier(Expression):
    def __init__(self, token: Token, value: str) -> None:
        super().__init__(token)

        self.value = value

    def __repr__(self) -> str:
        return self.value


class LetStatement(Statement):
    def __init__(self, token: Token, name: Identifier, expression: Expression) -> None:
        super().__init__(token)

        self.name = name
        self.expression = expression

    def __repr__(self) -> str:
        out = f"{self.token_literal()} {self.name} = "

        if self.expression is not None:
            out += f"{self.expression}"

        out += ";"

        return out


class ReturnStatement(Statement):
    def __init__(self, token: Token, return_value: Expression) -> None:
        super().__init__(token)

        self.return_value = return_value

    def __repr__(self) -> str:
        out = f"{self.token_literal()} "

        if self.return_value is not None:
            out += f"{self.return_value}"
        out += ";"

        return out


class ExpressionStatement(Statement):
    def __init__(self, token: Token, expression: Expression) -> None:
        super().__init__(token)

        self.expression = expression

    def __repr__(self) -> str:
        if self.expression is not None:
            return f"{self.expression}"
        return ""


class IntegerLiteral(Expression):
    def __init__(self, token: Token, value: int) -> None:
        super().__init__(token)

        self.value = value


class PrefixExpression(Expression):
    def __init__(self, token: Token, operator: str, right: Expression) -> None:
        super().__init__(token)

        self.operator = operator
        self.right = right

    def __repr__(self) -> str:
        return f"({self.operator}{self.right})"


class InfixExpression(Expression):
    def __init__(
        self,
        token: Token,
        left: Expression,
        operator: str,
        right: Expression,
    ) -> None:
        super().__init__(token)

        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self) -> str:
        return f"({self.left} {self.operator} {self.right})"
