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


class Boolean(Expression):
    def __init__(self, token: Token, value: bool) -> None:
        super().__init__(token)

        self.value = value

    def __repr__(self) -> str:
        return str(self.value).lower()


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


class BlockStatement(Statement):
    def __init__(self, token: Token, statements: list[Statement]) -> None:
        super().__init__(token)

        self.statements = statements or []

    def __repr__(self) -> str:
        out = ""

        for statement in self.statements:
            out += f"{statement}"

        return out


class IntegerLiteral(Expression):
    def __init__(self, token: Token, value: int) -> None:
        super().__init__(token)

        self.value = value

    def __repr__(self) -> str:
        return str(self.value)


class StringLiteral(Expression):
    def __init__(self, token: Token, value: str) -> None:
        super().__init__(token)

        self.value = value

    def __repr__(self) -> str:
        return self.token.literal


class FunctionLiteral(Expression):
    def __init__(
        self, token: Token, parameters: list[Identifier], body: BlockStatement
    ) -> None:
        super().__init__(token)

        self.parameters = parameters
        self.body = body

    def __repr__(self) -> str:
        out = f"{self.token_literal()}("

        params = []

        for param in self.parameters:
            params.append(f"{param}")

        out += ", ".join(params)
        out += ") "
        out += f"{self.body}"

        return out


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


class IfExpression(Expression):
    def __init__(
        self,
        token: Token,
        condition: Expression,
        consequence: BlockStatement,
        alternative: BlockStatement | None = None,
    ) -> None:
        super().__init__(token)

        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative

    def __repr__(self) -> str:
        out = f"if {self.condition} {self.consequence}"

        if self.alternative is not None:
            out += f" else {self.alternative}"

        return out


class CallExpression(Expression):
    def __init__(
        self, token: Token, function: Expression, arguments: list[Expression]
    ) -> None:
        super().__init__(token)

        self.function = function
        self.arguments = arguments

    def __repr__(self) -> str:
        out = f"{self.function}("

        args = []

        for arg in self.arguments:
            args.append(f"{arg}")

        out += ", ".join(args)
        out += ")"

        return out


class ArrayLiteral(Expression):
    def __init__(self, token: Token, elements: list[Expression]) -> None:
        super().__init__(token)

        self.elements = elements

    def __repr__(self) -> str:
        out = "["
        elements = []

        for element in self.elements:
            elements.append(f"{element}")

        out += ", ".join(elements)
        out += "]"

        return out


class IndexExpression(Expression):
    def __init__(self, token: Token, left: Expression, index: Expression) -> None:
        super().__init__(token)

        self.left = left
        self.index = index

    def __repr__(self) -> str:
        return f"({self.left}[{self.index}])"
