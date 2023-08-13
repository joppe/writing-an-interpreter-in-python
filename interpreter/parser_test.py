import unittest
from interpreter.ast import (
    InfixExpression,
    IntegerLiteral,
    LetStatement,
    PrefixExpression,
    Program,
    ReturnStatement,
    ExpressionStatement,
    Identifier,
)
from interpreter.lexer import Lexer
from interpreter.parser import Parser


class TestParser(unittest.TestCase):
    def test_return_statements(self) -> None:
        input = """
            return 5;
            return 10;
            return 993322;
        """
        program = self._setup_program(input)

        self.assertNotEqual(program, None)
        self.assertEqual(len(program.statements), 3)

        tests = ["5", "10", "993322"]

        for i, _ in enumerate(tests):
            stmt = program.statements[i]

            self.assertEqual(stmt.token_literal(), "return")
            self.assertIsInstance(stmt, ReturnStatement)

    def test_identifier_expression(self) -> None:
        input = "foobar;"
        program = self._setup_program(input)

        self.assertNotEqual(program, None)
        self.assertEqual(len(program.statements), 1)

        stmt = program.statements[0]

        self.assertIsInstance(stmt, ExpressionStatement)

        if isinstance(stmt, ExpressionStatement):
            self.assertIsInstance(stmt.expression, Identifier)

            if isinstance(stmt.expression, Identifier):
                self.assertEqual(stmt.expression.value, "foobar")
                self.assertEqual(stmt.expression.token_literal(), "foobar")

    def test_integer_literal_expression(self) -> None:
        input = "5;"
        program = self._setup_program(input)

        self.assertNotEqual(program, None)
        self.assertEqual(len(program.statements), 1)

        stmt = program.statements[0]

        self.assertIsInstance(stmt, ExpressionStatement)

        if isinstance(stmt, ExpressionStatement):
            self.assertIsInstance(stmt.expression, IntegerLiteral)

            if isinstance(stmt.expression, IntegerLiteral):
                self.assertEqual(stmt.expression.value, 5)
                self.assertEqual(stmt.expression.token_literal(), "5")

    def test_prefix_expressions(self) -> None:
        prefix_tests = [
            ("!5;", "!", 5),
            ("-15;", "-", 15),
        ]

        for tt in prefix_tests:
            program = self._setup_program(tt[0])

            self.assertNotEqual(program, None)
            self.assertEqual(len(program.statements), 1)

            stmt = program.statements[0]

            self.assertIsInstance(stmt, ExpressionStatement)

            if isinstance(stmt, ExpressionStatement):
                self.assertIsInstance(stmt.expression, PrefixExpression)

                if isinstance(stmt.expression, PrefixExpression):
                    self.assertEqual(stmt.expression.operator, tt[1])
                    self.assertIsInstance(stmt.expression.right, IntegerLiteral)

                    if isinstance(stmt.expression.right, IntegerLiteral):
                        self.assertEqual(stmt.expression.right.value, tt[2])
                        self.assertEqual(
                            stmt.expression.right.token_literal(), str(tt[2])
                        )

    def test_infix_expressions(self) -> None:
        infix_tests = [
            ("5 + 5;", 5, "+", 5),
            ("5 - 5;", 5, "-", 5),
            ("5 * 5;", 5, "*", 5),
            ("5 / 5;", 5, "/", 5),
            ("5 > 5;", 5, ">", 5),
            ("5 < 5;", 5, "<", 5),
            ("5 == 5;", 5, "==", 5),
            ("5 != 5;", 5, "!=", 5),
        ]

        for tt in infix_tests:
            program = self._setup_program(tt[0])

            self.assertNotEqual(program, None)
            self.assertEqual(len(program.statements), 1)

            stmt = program.statements[0]

            self.assertIsInstance(stmt, ExpressionStatement)

            if isinstance(stmt, ExpressionStatement):
                self.assertIsInstance(stmt.expression, InfixExpression)

                if isinstance(stmt.expression, InfixExpression):
                    self.assertIsInstance(stmt.expression.left, IntegerLiteral)

                    if isinstance(stmt.expression.left, IntegerLiteral):
                        self.assertEqual(stmt.expression.left.value, tt[1])
                        self.assertEqual(
                            stmt.expression.left.token_literal(), str(tt[1])
                        )

                    self.assertEqual(stmt.expression.operator, tt[2])

                    self.assertIsInstance(stmt.expression.right, IntegerLiteral)

                    if isinstance(stmt.expression.right, IntegerLiteral):
                        self.assertEqual(stmt.expression.right.value, tt[3])
                        self.assertEqual(
                            stmt.expression.right.token_literal(), str(tt[3])
                        )

    def test_operator_precedence_parsing(self) -> None:
        tests = [
            ("-a * b", "((-a) * b)"),
            ("!-a", "(!(-a))"),
            ("a + b + c", "((a + b) + c)"),
            ("a + b - c", "((a + b) - c)"),
            ("a * b * c", "((a * b) * c)"),
            ("a * b / c", "((a * b) / c)"),
            ("a + b / c", "(a + (b / c))"),
            ("a + b * c + d / e - f", "(((a + (b * c)) + (d / e)) - f)"),
            ("3 + 4; -5 * 5", "(3 + 4)((-5) * 5)"),
            ("5 > 4 == 3 < 4", "((5 > 4) == (3 < 4))"),
            ("5 < 4 != 3 > 4", "((5 < 4) != (3 > 4))"),
            ("3 + 4 * 5 == 3 * 1 + 4 * 5", "((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))"),
        ]

        for tt in tests:
            program = self._setup_program(tt[0])

            self.assertNotEqual(program, None)
            self.assertEqual(str(program), tt[1])

    def test_let_statements(self) -> None:
        input = """
            let x = 5;
            let y = 10;
            let foobar = 838383;
        """
        program = self._setup_program(input)

        self.assertNotEqual(program, None)
        self.assertEqual(len(program.statements), 3)

        tests = ["x", "y", "foobar"]

        for i, tt in enumerate(tests):
            stmt = program.statements[i]

            self.assertEqual(stmt.token_literal(), "let")
            self.assertIsInstance(stmt, LetStatement)

            if isinstance(stmt, LetStatement):
                self.assertEqual(stmt.name.value, tt)
                self.assertEqual(stmt.name.token_literal(), tt)

    def _setup_program(self, input: str) -> Program:
        lexer = Lexer(input)
        parser = Parser(lexer)
        program = parser.parse_program()

        parser_errors = parser.errors()

        if len(parser_errors) != 0:
            for error in parser_errors:
                print(f"parser error: {error}")

        return program
