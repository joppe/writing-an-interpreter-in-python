import unittest
from typing import Any
from interpreter.ast import (
    ArrayLiteral,
    Boolean,
    CallExpression,
    Expression,
    FunctionLiteral,
    HashLiteral,
    IfExpression,
    IndexExpression,
    InfixExpression,
    IntegerLiteral,
    LetStatement,
    PrefixExpression,
    Program,
    ReturnStatement,
    ExpressionStatement,
    Identifier,
    StringLiteral,
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
            self._test_identifier(stmt.expression, "foobar")

    def test_boolean_expression(self) -> None:
        input = "true;"
        program = self._setup_program(input)

        self.assertNotEqual(program, None)
        self.assertEqual(len(program.statements), 1)

        stmt = program.statements[0]

        self.assertIsInstance(stmt, ExpressionStatement)

        if isinstance(stmt, ExpressionStatement):
            self.assertIsInstance(stmt.expression, Boolean)

            if isinstance(stmt.expression, Boolean):
                self.assertEqual(stmt.expression.value, True)
                self.assertEqual(stmt.expression.token_literal(), "true")

    def test_integer_literal_expression(self) -> None:
        input = "5;"
        program = self._setup_program(input)

        self.assertNotEqual(program, None)
        self.assertEqual(len(program.statements), 1)

        stmt = program.statements[0]

        self.assertIsInstance(stmt, ExpressionStatement)

        if isinstance(stmt, ExpressionStatement):
            self._test_integer_literal(stmt.expression, 5)

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
                    self._test_integer_literal(stmt.expression.right, tt[2])

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
            ("true == true", True, "==", True),
            ("true != false", True, "!=", False),
            ("false == false", False, "==", False),
        ]

        for tt in infix_tests:
            program = self._setup_program(tt[0])

            self.assertNotEqual(program, None)
            self.assertEqual(len(program.statements), 1)

            stmt = program.statements[0]

            self.assertIsInstance(stmt, ExpressionStatement)

            if isinstance(stmt, ExpressionStatement):
                self._test_infix_expression(stmt.expression, tt[1], tt[2], tt[3])

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
            ("true", "true"),
            ("false", "false"),
            ("3 > 5 == false", "((3 > 5) == false)"),
            ("3 < 5 == true", "((3 < 5) == true)"),
            ("1 + (2 + 3) + 4", "((1 + (2 + 3)) + 4)"),
            ("(5 + 5) * 2", "((5 + 5) * 2)"),
            ("2 / (5 + 5)", "(2 / (5 + 5))"),
            ("-(5 + 5)", "(-(5 + 5))"),
            ("!(true == true)", "(!(true == true))"),
            ("a + add(b * c) + d", "((a + add((b * c))) + d)"),
            (
                "add(a, b, 1, 2 * 3, 4 + 5, add(6, 7 * 8))",
                "add(a, b, 1, (2 * 3), (4 + 5), add(6, (7 * 8)))",
            ),
            ("add(a + b + c * d / f + g)", "add((((a + b) + ((c * d) / f)) + g))"),
            ("a * [1, 2, 3, 4][b * c] * d", "((a * ([1, 2, 3, 4][(b * c)])) * d)"),
            (
                "add(a * b[2], b[1], 2 * [1, 2][1])",
                "add((a * (b[2])), (b[1]), (2 * ([1, 2][1])))",
            ),
        ]

        for tt in tests:
            program = self._setup_program(tt[0])

            self.assertNotEqual(program, None)
            self.assertEqual(str(program), tt[1])

    def test_if_expression(self) -> None:
        input = "if (x < y) { x }"
        program = self._setup_program(input)

        self.assertNotEqual(program, None)
        self.assertEqual(len(program.statements), 1)

        stmt = program.statements[0]

        self.assertIsInstance(stmt, ExpressionStatement)

        if isinstance(stmt, ExpressionStatement):
            expression = stmt.expression

            self.assertIsInstance(expression, IfExpression)

            if isinstance(expression, IfExpression):
                self._test_infix_expression(expression.condition, "x", "<", "y")

                self.assertEqual(len(expression.consequence.statements), 1)

                consequence = expression.consequence.statements[0]

                self.assertIsInstance(consequence, ExpressionStatement)

                if isinstance(consequence, ExpressionStatement):
                    self._test_identifier(consequence.expression, "x")

                self.assertEqual(expression.alternative, None)

    def test_function_literal_parsing(self) -> None:
        input = "fn(x, y) { x + y; }"
        program = self._setup_program(input)

        self.assertNotEqual(program, None)
        self.assertEqual(len(program.statements), 1)

        stmt = program.statements[0]

        self.assertIsInstance(stmt, ExpressionStatement)

        if isinstance(stmt, ExpressionStatement):
            function = stmt.expression

            self.assertIsInstance(function, FunctionLiteral)

            if isinstance(function, FunctionLiteral):
                self.assertEqual(len(function.parameters), 2)

                self._test_literal_expression(function.parameters[0], "x")
                self._test_literal_expression(function.parameters[1], "y")

                self.assertEqual(len(function.body.statements), 1)

                body_stmt = function.body.statements[0]

                self.assertIsInstance(body_stmt, ExpressionStatement)

                if isinstance(body_stmt, ExpressionStatement):
                    self._test_infix_expression(body_stmt.expression, "x", "+", "y")

    def test_function_parameter_parsing(self) -> None:
        tests: list[tuple[str, list[str]]] = [
            ("fn() {};", []),
            ("fn(x) {};", ["x"]),
            ("fn(x, y, z) {};", ["x", "y", "z"]),
        ]

        for tt in tests:
            program = self._setup_program(tt[0])

            self.assertNotEqual(program, None)
            self.assertEqual(len(program.statements), 1)

            stmt = program.statements[0]

            self.assertIsInstance(stmt, ExpressionStatement)

            if isinstance(stmt, ExpressionStatement):
                function = stmt.expression

                self.assertIsInstance(function, FunctionLiteral)

                if isinstance(function, FunctionLiteral):
                    self.assertEqual(len(function.parameters), len(tt[1]))

                    for i, param in enumerate(tt[1]):
                        self._test_literal_expression(function.parameters[i], param)

    def test_call_expression_parsing(self) -> None:
        input = "add(1, 2 * 3, 4 + 5);"
        program = self._setup_program(input)

        self.assertNotEqual(program, None)
        self.assertEqual(len(program.statements), 1)

        stmt = program.statements[0]

        self.assertIsInstance(stmt, ExpressionStatement)

        if isinstance(stmt, ExpressionStatement):
            expression = stmt.expression

            self.assertIsInstance(expression, CallExpression)

            if isinstance(expression, CallExpression):
                self._test_identifier(expression.function, "add")

                self.assertEqual(len(expression.arguments), 3)

                self._test_literal_expression(expression.arguments[0], 1)
                self._test_infix_expression(expression.arguments[1], 2, "*", 3)
                self._test_infix_expression(expression.arguments[2], 4, "+", 5)

    def test_let_statements(self) -> None:
        tests = [
            ("let x = 5;", "x", 5),
            ("let y = true;", "y", True),
            ("let foobar = y;", "foobar", "y"),
        ]

        for tt in tests:
            program = self._setup_program(tt[0])

            self.assertNotEqual(program, None)
            self.assertEqual(len(program.statements), 1)

            stmt = program.statements[0]

            self.assertIsInstance(stmt, LetStatement)

            if isinstance(stmt, LetStatement):
                self.assertEqual(stmt.name.value, tt[1])

                if stmt.expression is not None:
                    self._test_literal_expression(stmt.expression, tt[2])

    def test_string_literal_expression(self) -> None:
        input = '"hello world";'
        program = self._setup_program(input)

        self.assertNotEqual(program, None)
        self.assertEqual(len(program.statements), 1)

        stmt = program.statements[0]

        self.assertIsInstance(stmt, ExpressionStatement)

        if isinstance(stmt, ExpressionStatement):
            expression = stmt.expression

            self.assertIsInstance(expression, StringLiteral)

            if isinstance(expression, StringLiteral):
                self.assertEqual(expression.value, "hello world")

    def test_parsing_array_literals(self) -> None:
        input = "[1, 2 * 2, 3 + 3]"
        program = self._setup_program(input)

        self.assertNotEqual(program, None)
        self.assertEqual(len(program.statements), 1)

        stmt = program.statements[0]

        self.assertIsInstance(stmt, ExpressionStatement)

        if isinstance(stmt, ExpressionStatement):
            expression = stmt.expression

            self.assertIsInstance(expression, ArrayLiteral)

            if isinstance(expression, ArrayLiteral):
                self.assertEqual(len(expression.elements), 3)

                self._test_integer_literal(expression.elements[0], 1)
                self._test_infix_expression(expression.elements[1], 2, "*", 2)
                self._test_infix_expression(expression.elements[2], 3, "+", 3)

    def test_parsing_index_expressions(self) -> None:
        input = "myArray[1 + 1]"
        program = self._setup_program(input)

        self.assertNotEqual(program, None)
        self.assertEqual(len(program.statements), 1)

        stmt = program.statements[0]

        self.assertIsInstance(stmt, ExpressionStatement)

        if isinstance(stmt, ExpressionStatement):
            expression = stmt.expression

            self.assertIsInstance(expression, IndexExpression)

            if isinstance(expression, IndexExpression):
                self._test_identifier(expression.left, "myArray")
                self._test_infix_expression(expression.index, 1, "+", 1)

    def test_parsing_hash_literals_string_keys(self) -> None:
        input = '{"one": 1, "two": 2, "three": 3}'
        program = self._setup_program(input)

        self.assertNotEqual(program, None)
        self.assertEqual(len(program.statements), 1)

        stmt = program.statements[0]

        self.assertIsInstance(stmt, ExpressionStatement)

        if isinstance(stmt, ExpressionStatement):
            expression = stmt.expression

            self.assertIsInstance(expression, HashLiteral)

            if isinstance(expression, HashLiteral):
                self.assertEqual(len(expression.pairs), 3)

                expected = {"one": 1, "two": 2, "three": 3}

                for key, value in expression.pairs.items():
                    self.assertIsInstance(key, StringLiteral)

                    if isinstance(key, StringLiteral):
                        expected_value = expected[key.value]

                        self._test_integer_literal(value, expected_value)

    def test_parsing_empty_hash_literal(self) -> None:
        input = "{}"
        program = self._setup_program(input)

        self.assertNotEqual(program, None)
        self.assertEqual(len(program.statements), 1)

        stmt = program.statements[0]

        self.assertIsInstance(stmt, ExpressionStatement)

        if isinstance(stmt, ExpressionStatement):
            expression = stmt.expression

            self.assertIsInstance(expression, HashLiteral)

            if isinstance(expression, HashLiteral):
                self.assertEqual(len(expression.pairs), 0)

    def test_parsing_hash_literals_with_expressions(self) -> None:
        input = '{"one": 0 + 1, "two": 10 - 8, "three": 15 / 5}'
        program = self._setup_program(input)

        self.assertNotEqual(program, None)
        self.assertEqual(len(program.statements), 1)

        stmt = program.statements[0]

        self.assertIsInstance(stmt, ExpressionStatement)

        if isinstance(stmt, ExpressionStatement):
            expression = stmt.expression

            self.assertIsInstance(expression, HashLiteral)

            if isinstance(expression, HashLiteral):
                self.assertEqual(len(expression.pairs), 3)

                tests = {
                    "one": lambda e: self._test_infix_expression(e, 0, "+", 1),
                    "two": lambda e: self._test_infix_expression(e, 10, "-", 8),
                    "three": lambda e: self._test_infix_expression(e, 15, "/", 5),
                }

                for key, value in expression.pairs.items():
                    self.assertIsInstance(key, StringLiteral)

                    if isinstance(key, StringLiteral):
                        test_func = tests[key.value]

                        test_func(value)

    def _test_integer_literal(self, expression: Expression, value: int) -> None:
        self.assertIsInstance(expression, IntegerLiteral)

        if isinstance(expression, IntegerLiteral):
            self.assertEqual(expression.value, value)
            self.assertEqual(expression.token_literal(), str(value))

    def _test_identifier(self, expression: Expression, value: str) -> None:
        self.assertIsInstance(expression, Identifier)

        if isinstance(expression, Identifier):
            self.assertEqual(expression.value, value)
            self.assertEqual(expression.token_literal(), value)

    def _test_literal_expression(self, expression: Expression, expected: Any) -> None:
        # First check for boolean, then integer because bool is a subclass of int
        if isinstance(expected, bool):
            self._test_boolean_literal(expression, expected)
        elif isinstance(expected, int):
            self._test_integer_literal(expression, expected)
        elif isinstance(expected, str):
            self._test_identifier(expression, expected)
        else:
            self.fail(f"type of expression not handled, got={type(expression)}")

    def _test_boolean_literal(self, expression: Expression, value: bool) -> None:
        self.assertIsInstance(expression, Boolean)

        if isinstance(expression, Boolean):
            self.assertEqual(expression.value, value)
            self.assertEqual(expression.token_literal(), str(value).lower())

    def _test_infix_expression(
        self, expression: Expression, left: Any, operator: str, right: Any
    ) -> None:
        self.assertIsInstance(expression, InfixExpression)

        if isinstance(expression, InfixExpression):
            self._test_literal_expression(expression.left, left)
            self.assertEqual(expression.operator, operator)
            self._test_literal_expression(expression.right, right)

    def _setup_program(self, input: str) -> Program:
        lexer = Lexer(input)
        parser = Parser(lexer)
        program = parser.parse_program()

        parser_errors = parser.errors()

        if len(parser_errors) != 0:
            for error in parser_errors:
                print(f"parser error: {error}")

        return program
