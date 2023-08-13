import unittest

from interpreter.ast import Program, LetStatement, Identifier
from interpreter.token import Token
from interpreter.token_type import TokenType


class AstTest(unittest.TestCase):
    def test_to_string(self) -> None:
        program = Program(
            [
                LetStatement(
                    Token(TokenType.LET, "let"),
                    Identifier(
                        Token(TokenType.IDENT, "myVar"),
                        "myVar",
                    ),
                    Identifier(
                        Token(TokenType.IDENT, "anotherVar"),
                        "anotherVar",
                    ),
                ),
            ]
        )

        self.assertEqual(f"{program}", "let myVar = anotherVar;")
