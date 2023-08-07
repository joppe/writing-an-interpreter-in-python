from typing import Optional
from interpreter.ast import Expression, Identifier, LetStatement, Program, Statement
from interpreter.lexer import Lexer
from interpreter.token import Token
from interpreter.token_type import TokenType


class Parser:
    def __init__(self, lexer: Lexer):
        self._lexer = lexer
        self._errors: list[str] = []
        self._current_token: Token = Token(TokenType.ILLEGAL, "")
        self._peek_token: Token = Token(TokenType.ILLEGAL, "")

        self._next_token()
        self._next_token()

    def parse_program(self) -> Program:
        program = Program()

        while not self._current_token_is(TokenType.EOF):
            statement = self._parse_statement()

            if statement is not None:
                program.statements.append(statement)

            self._next_token()

        return program

    def errors(self) -> list[str]:
        return self._errors

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
            case _:
                return None

    def _parse_let_statement(self) -> Optional[LetStatement]:
        token = self._current_token

        if self._expect_peek(TokenType.IDENT) is False:
            return None

        name = Identifier(self._current_token, self._current_token.literal)

        if self._expect_peek(TokenType.ASSIGN) is False:
            return None

        while not self._current_token_is(TokenType.SEMICOLON):
            self._next_token()

        statement = LetStatement(token, name, Expression(token))

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
