from typing import Optional, Callable
from interpreter.ast import (
    ArrayLiteral,
    BlockStatement,
    Boolean,
    CallExpression,
    Expression,
    ExpressionStatement,
    FunctionLiteral,
    Identifier,
    IfExpression,
    IndexExpression,
    InfixExpression,
    IntegerLiteral,
    LetStatement,
    PrefixExpression,
    Program,
    ReturnStatement,
    Statement,
    StringLiteral,
)
from interpreter.lexer import Lexer
from interpreter.token import Token
from interpreter.token_type import TokenType
from enum import Enum


class Precedence(Enum):
    LOWEST = 1
    EQUALS = 2
    LESSGREATER = 3
    SUM = 4
    PRODUCT = 5
    PREFIX = 6
    CALL = 7
    INDEX = 8


PRECEDENCES: dict[TokenType, Precedence] = {
    TokenType.EQ: Precedence.EQUALS,
    TokenType.NOT_EQ: Precedence.EQUALS,
    TokenType.LT: Precedence.LESSGREATER,
    TokenType.GT: Precedence.LESSGREATER,
    TokenType.PLUS: Precedence.SUM,
    TokenType.MINUS: Precedence.SUM,
    TokenType.SLASH: Precedence.PRODUCT,
    TokenType.ASTERISK: Precedence.PRODUCT,
    TokenType.LPAREN: Precedence.CALL,
    TokenType.LBRACKET: Precedence.INDEX,
}


class Parser:
    def __init__(self, lexer: Lexer) -> None:
        self._lexer = lexer
        self._errors: list[str] = []
        self._current_token: Token = Token(TokenType.ILLEGAL, "")
        self._peek_token: Token = Token(TokenType.ILLEGAL, "")
        self._prefix_parse_fns: dict[TokenType, Callable] = {
            TokenType.IDENT: self._parse_identifier,
            TokenType.INT: self._parse_integer_literal,
            TokenType.BANG: self._parse_prefix_expression,
            TokenType.MINUS: self._parse_prefix_expression,
            TokenType.TRUE: self._parse_boolean,
            TokenType.FALSE: self._parse_boolean,
            TokenType.LPAREN: self._parse_grouped_expression,
            TokenType.IF: self._parse_if_expression,
            TokenType.FUNCTION: self._parse_function_literal,
            TokenType.STRING: self._parse_string_literal,
            TokenType.LBRACKET: self._parse_array_literal,
        }
        self._infix_parse_fns: dict[TokenType, Callable] = {
            TokenType.PLUS: self._parse_infix_expression,
            TokenType.MINUS: self._parse_infix_expression,
            TokenType.SLASH: self._parse_infix_expression,
            TokenType.ASTERISK: self._parse_infix_expression,
            TokenType.EQ: self._parse_infix_expression,
            TokenType.NOT_EQ: self._parse_infix_expression,
            TokenType.LT: self._parse_infix_expression,
            TokenType.GT: self._parse_infix_expression,
            TokenType.LPAREN: self._parse_call_expression,
            TokenType.LBRACKET: self._parse_index_expression,
        }

        self._next_token()
        self._next_token()

    def parse_program(self) -> Program:
        statements: list[Statement] = []

        while not self._current_token_is(TokenType.EOF):
            statement = self._parse_statement()

            if statement is not None:
                statements.append(statement)

            self._next_token()

        return Program(statements)

    def errors(self) -> list[str]:
        return self._errors

    def _parse_index_expression(self, left: Expression) -> Optional[Expression]:
        token = self._current_token

        self._next_token()

        index = self._parse_expression(Precedence.LOWEST)

        if index is None:
            return None

        if not self._expect_peek(TokenType.RBRACKET):
            return None

        return IndexExpression(token, left, index)

    def _parse_array_literal(self) -> Expression:
        token = self._current_token
        elements = self._parse_expression_list(TokenType.RBRACKET)

        return ArrayLiteral(token, elements)

    def _parse_expression_list(self, end: TokenType) -> list[Expression]:
        expressions: list[Expression] = []

        if self._peek_token_is(end):
            self._next_token()

            return expressions

        self._next_token()

        expression = self._parse_expression(Precedence.LOWEST)

        if expression is not None:
            expressions.append(expression)

        while self._peek_token_is(TokenType.COMMA):
            self._next_token()
            self._next_token()

            expression = self._parse_expression(Precedence.LOWEST)

            if expression is not None:
                expressions.append(expression)

        if not self._expect_peek(end):
            return []

        return expressions

    def _parse_string_literal(self) -> Expression:
        return StringLiteral(self._current_token, self._current_token.literal)

    def _peek_precedence(self) -> Precedence:
        precedence = PRECEDENCES.get(self._peek_token.token_type)

        if precedence is None:
            return Precedence.LOWEST

        return precedence

    def _current_precedence(self) -> Precedence:
        precedence = PRECEDENCES.get(self._current_token.token_type)

        if precedence is None:
            return Precedence.LOWEST

        return precedence

    def _peek_error(self, token_type: TokenType) -> None:
        peek_type = self._peek_token.token_type
        message = f"expected next token to be {token_type}, got {peek_type} instead"

        self._errors.append(message)

    def _next_token(self):
        self._current_token = self._peek_token
        self._peek_token = self._lexer.next_token()

    def _parse_statement(self) -> Optional[Statement]:
        match self._current_token.token_type:
            case TokenType.LET:
                return self._parse_let_statement()
            case TokenType.RETURN:
                return self._parse_return_statment()
            case _:
                return self._parse_expression_statement()

    def _parse_expression_statement(self) -> Optional[ExpressionStatement]:
        token = self._current_token
        expression = self._parse_expression(Precedence.LOWEST)

        if expression is None:
            return None

        if self._peek_token_is(TokenType.SEMICOLON):
            self._next_token()

        return ExpressionStatement(token, expression)

    def _parse_expression(self, precedence: Precedence) -> Optional[Expression]:
        prefix = self._prefix_parse_fns.get(self._current_token.token_type)

        if prefix is None:
            self._errors.append(f"no prefix parse function for {self._current_token}")
            return None

        left_expression = prefix()

        while (
            not self._peek_token_is(TokenType.SEMICOLON)
            and precedence.value < self._peek_precedence().value
        ):
            infix = self._infix_parse_fns.get(self._peek_token.token_type)

            if infix is None:
                return left_expression

            self._next_token()

            left_expression = infix(left_expression)

        return left_expression

    def _parse_identifier(self) -> Identifier:
        return Identifier(self._current_token, self._current_token.literal)

    def _parse_boolean(self) -> Boolean:
        return Boolean(self._current_token, self._current_token_is(TokenType.TRUE))

    def _parse_grouped_expression(self) -> Optional[Expression]:
        self._next_token()

        expression = self._parse_expression(Precedence.LOWEST)

        if not self._expect_peek(TokenType.RPAREN):
            return None

        return expression

    def _parse_if_expression(self) -> Optional[Expression]:
        token = self._current_token

        if not self._expect_peek(TokenType.LPAREN):
            return None

        self._next_token()

        condition = self._parse_expression(Precedence.LOWEST)

        if condition is None:
            return None

        if not self._expect_peek(TokenType.RPAREN):
            return None

        if not self._expect_peek(TokenType.LBRACE):
            return None

        consequence = self._parse_block_statement()

        alternative = None

        if self._peek_token_is(TokenType.ELSE):
            self._next_token()

            if not self._expect_peek(TokenType.LBRACE):
                return None

            alternative = self._parse_block_statement()

        return IfExpression(token, condition, consequence, alternative)

    def _parse_function_literal(self) -> Optional[Expression]:
        token = self._current_token

        if not self._expect_peek(TokenType.LPAREN):
            return None

        parameters = self._parse_function_parameters()

        if not self._expect_peek(TokenType.LBRACE):
            return None

        body = self._parse_block_statement()

        return FunctionLiteral(token, parameters, body)

    def _parse_function_parameters(self) -> list[Identifier]:
        identifiers: list[Identifier] = []

        if self._peek_token_is(TokenType.RPAREN):
            self._next_token()

            return identifiers

        self._next_token()

        identifier = Identifier(self._current_token, self._current_token.literal)
        identifiers.append(identifier)

        while self._peek_token_is(TokenType.COMMA):
            self._next_token()
            self._next_token()

            identifier = Identifier(self._current_token, self._current_token.literal)
            identifiers.append(identifier)

        if not self._expect_peek(TokenType.RPAREN):
            return []

        return identifiers

    def _parse_call_expression(self, function: Expression) -> Optional[Expression]:
        token = self._current_token
        arguments = self._parse_expression_list(TokenType.RPAREN)

        return CallExpression(token, function, arguments)

    def _parse_block_statement(self) -> BlockStatement:
        token = self._current_token
        statements: list[Statement] = []

        self._next_token()

        while not self._current_token_is(
            TokenType.RBRACE
        ) and not self._current_token_is(TokenType.EOF):
            statement = self._parse_statement()

            if statement is not None:
                statements.append(statement)

            self._next_token()

        return BlockStatement(token, statements)

    def _parse_integer_literal(self) -> Optional[Expression]:
        token = self._current_token

        try:
            value = int(token.literal)
        except ValueError:
            message = f"could not parse {token.literal} as integer"
            self._errors.append(message)
            return None

        expression = IntegerLiteral(token, value)

        return expression

    def _parse_prefix_expression(self) -> Optional[Expression]:
        token = self._current_token
        operator = token.literal

        self._next_token()

        right = self._parse_expression(Precedence.PREFIX)

        if right is None:
            return None

        return PrefixExpression(token, operator, right)

    def _parse_infix_expression(self, left: Expression) -> Optional[Expression]:
        token = self._current_token
        operator = token.literal
        precedence = self._current_precedence()

        self._next_token()

        right = self._parse_expression(precedence)

        if right is None:
            return None

        return InfixExpression(token, left, operator, right)

    def _parse_return_statment(self) -> Optional[Statement]:
        token = self._current_token

        self._next_token()

        return_value = self._parse_expression(Precedence.LOWEST)

        if return_value is None:
            return None

        statement = ReturnStatement(token, return_value)

        if self._peek_token_is(TokenType.SEMICOLON):
            self._next_token()

        return statement

    def _parse_let_statement(self) -> Optional[LetStatement]:
        token = self._current_token

        if self._expect_peek(TokenType.IDENT) is False:
            return None

        name = Identifier(self._current_token, self._current_token.literal)

        if self._expect_peek(TokenType.ASSIGN) is False:
            return None

        self._next_token()

        value = self._parse_expression(Precedence.LOWEST)

        if self._peek_token_is(TokenType.SEMICOLON):
            self._next_token()

        statement = LetStatement(token, name, value)

        return statement

    def _current_token_is(self, token_type: TokenType) -> bool:
        return self._current_token.token_type == token_type

    def _peek_token_is(self, token_type: TokenType) -> bool:
        return self._peek_token.token_type == token_type

    def _expect_peek(self, token_type: TokenType) -> bool:
        if self._peek_token_is(token_type):
            self._next_token()

            return True
        else:
            self._peek_error(token_type)

            return False
