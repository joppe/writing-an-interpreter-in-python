import unittest

from typing import cast
from interpreter.object import Boolean, Object, Integer
from interpreter.lexer import Lexer
from interpreter.parser import Parser
from interpreter.eval import Eval


class TestEval(unittest.TestCase):
    def test_eval_integer_expression(self) -> None:
        tests = [
            ("5", 5),
            ("10", 10),
            ("-5", -5),
            ("-10", -10),
            ("5 + 5 + 5 + 5 - 10", 10),
            ("2 * 2 * 2 * 2 * 2", 32),
            ("-50 + 100 + -50", 0),
            ("5 * 2 + 10", 20),
            ("5 + 2 * 10", 25),
            ("20 + 2 * -10", 0),
            ("50 / 2 * 2 + 10", 60),
            ("2 * (5 + 10)", 30),
            ("3 * 3 * 3 + 10", 37),
            ("3 * (3 * 3) + 10", 37),
            ("(5 + 10 * 2 + 15 / 3) * 2 + -10", 50),
        ]

        for tt in tests:
            evaluated = self._test_eval(tt[0])
            self._test_integer_object(evaluated, tt[1])

    def test_boolean_expression(self) -> None:
        tests = [
            ("true", True),
            ("false", False),
            ("1 < 2", True),
            ("1 > 2", False),
            ("1 < 1", False),
            ("1 > 1", False),
            ("1 == 1", True),
            ("1 != 1", False),
            ("1 == 2", False),
            ("1 != 2", True),
            ("true == true", True),
            ("false == false", True),
            ("true == false", False),
            ("true != false", True),
            ("false != true", True),
            ("(1 < 2) == true", True),
            ("(1 < 2) == false", False),
            ("(1 > 2) == true", False),
            ("(1 > 2) == false", True),
        ]

        for tt in tests:
            evaluated = self._test_eval(tt[0])
            self._test_boolean_object(evaluated, tt[1])

    def test_bang_operator(self) -> None:
        tests = [
            ("!true", False),
            ("!false", True),
            ("!5", False),
            ("!!true", True),
            ("!!false", False),
            ("!!5", True),
        ]

        for tt in tests:
            evaluated = self._test_eval(tt[0])
            self._test_boolean_object(evaluated, tt[1])

    def test_if_else_expressions(self) -> None:
        tests = [
            ("if (true) { 10 }", 10),
            ("if (false) { 10 }", None),
            ("if (1) { 10 }", 10),
            ("if (1 < 2) { 10 }", 10),
            ("if (1 > 2) { 10 }", None),
            ("if (1 > 2) { 10 } else { 20 }", 20),
            ("if (1 < 2) { 10 } else { 20 }", 10),
        ]

        for tt in tests:
            evaluated = self._test_eval(tt[0])

            if isinstance(tt[1], int):
                self._test_integer_object(evaluated, tt[1])
            else:
                self._test_null_object(evaluated)

    def test_return_statements(self) -> None:
        tests = [
            ("return 10;", 10),
            ("return 10; 9;", 10),
            ("return 2 * 5; 9;", 10),
            ("9; return 2 * 5; 9;", 10),
            (
                """
            if (10 > 1) {
                if (10 > 1) {
                    return 10;
                }

                return 1;
            }
            """,
                10,
            ),
        ]

        for tt in tests:
            evaluated = self._test_eval(tt[0])
            self._test_integer_object(evaluated, tt[1])

    def _test_null_object(self, obj: Object) -> None:
        self.assertEqual(obj, Eval.null)

    def _test_eval(self, input: str) -> Object:
        lexer = Lexer(input)
        parser = Parser(lexer)
        program = parser.parse_program()
        eval = Eval()

        evaluated = eval.eval(program)
        self.assertNotEqual(evaluated, None)

        return evaluated

    def _test_integer_object(self, obj: Object, expected: int) -> None:
        self.assertIsInstance(obj, Integer)
        self.assertEqual(cast(Integer, obj).value, expected)

    def _test_boolean_object(self, obj: Object, expected: bool) -> None:
        self.assertIsInstance(obj, Boolean)
        self.assertEqual(cast(Boolean, obj).value, expected)
