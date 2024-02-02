import unittest

from typing import cast, Dict
from interpreter import object
from interpreter.lexer import Lexer
from interpreter.parser import Parser
from interpreter.eval import Eval
from interpreter.environment import Environment


class TestEval(unittest.TestCase):
    def test_integer_expression(self) -> None:
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

    def test_string_liter(self) -> None:
        input = '"Hello World!"'

        evaluated = self._test_eval(input)

        self.assertIsInstance(evaluated, object.String)
        self.assertEqual(cast(object.String, evaluated).value, "Hello World!")

    def test_string_concatenation(self) -> None:
        input = '"Hello" + " " + "World!"'

        evaluated = self._test_eval(input)

        self.assertIsInstance(evaluated, object.String)
        self.assertEqual(cast(object.String, evaluated).value, "Hello World!")

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

    def test_error_handling(self) -> None:
        tests = [
            ("5 + true;", "type mismatch: INTEGER + BOOLEAN"),
            ("5 + true; 5;", "type mismatch: INTEGER + BOOLEAN"),
            ("-true", "unknown operator: -BOOLEAN"),
            ("true + false;", "unknown operator: BOOLEAN + BOOLEAN"),
            ("5; true + false; 5", "unknown operator: BOOLEAN + BOOLEAN"),
            (
                "if (10 > 1) { true + false; }",
                "unknown operator: BOOLEAN + BOOLEAN",
            ),
            (
                """
            if (10 > 1) {
                if (10 > 1) {
                    return true + false;
                }

                return 1;
            }
            """,
                "unknown operator: BOOLEAN + BOOLEAN",
            ),
            ("foobar", "identifier not found: foobar"),
            ('"Hello" - "World"', "unknown operator: STRING - STRING"),
            (
                '{"name": "Monkey"}[fn(x) { x }];',
                "unusable as hash key: FUNCTION",
            ),
        ]

        for tt in tests:
            evaluated = self._test_eval(tt[0])

            self.assertIsInstance(evaluated, object.Error)
            self.assertEqual(cast(object.Error, evaluated).message, tt[1])

    def test_let_statements(self) -> None:
        tests = [
            ("let a = 5; a;", 5),
            ("let a = 5 * 5; a;", 25),
            ("let a = 5; let b = a; b;", 5),
            ("let a = 5; let b = a; let c = a + b + 5; c;", 15),
        ]

        for tt in tests:
            evaluated = self._test_eval(tt[0])

            self._test_integer_object(evaluated, tt[1])

    def test_function_object(self) -> None:
        input = "fn(x) { x + 2; };"

        evaluated = self._test_eval(input)

        self.assertIsInstance(evaluated, object.Function)
        self.assertEqual(len(cast(object.Function, evaluated).parameters), 1)
        self.assertEqual(str(cast(object.Function, evaluated).parameters[0]), "x")
        self.assertEqual(str(cast(object.Function, evaluated).body), "(x + 2)")

    def test_function_application(self) -> None:
        tests = [
            ("let identity = fn(x) { x; }; identity(5);", 5),
            ("let identity = fn(x) { return x; }; identity(5);", 5),
            ("let double = fn(x) { x * 2; }; double(5);", 10),
            ("let add = fn(x, y) { x + y; }; add(5, 5);", 10),
            ("let add = fn(x, y) { x + y; }; add(5 + 5, add(5, 5));", 20),
            ("fn(x) { x; }(5)", 5),
        ]

        for tt in tests:
            evaluated = self._test_eval(tt[0])

            self._test_integer_object(evaluated, tt[1])

    def test_closures(self) -> None:
        input = """
        let newAdder = fn(x) {
            fn(y) { x + y };
        };

        let addTwo = newAdder(2);
        addTwo(2);
        """

        evaluated = self._test_eval(input)

        self._test_integer_object(evaluated, 4)

    def test_builtin_functions(self) -> None:
        tests = [
            ('len("")', 0),
            ('len("four")', 4),
            ('len("hello world")', 11),
            ("len(1)", "argument to `len` not supported, got ObjectType.INTEGER"),
            ('len("one", "two")', "wrong number of arguments. got=2, want=1"),
        ]

        for tt in tests:
            evaluated = self._test_eval(tt[0])

            if isinstance(tt[1], int):
                self._test_integer_object(evaluated, tt[1])
            else:
                self.assertIsInstance(evaluated, object.Error)
                self.assertEqual(cast(object.Error, evaluated).message, tt[1])

    def test_array_literals(self) -> None:
        input = "[1, 2 * 2, 3 + 3]"

        evaluated = self._test_eval(input)

        self.assertIsInstance(evaluated, object.Array)
        self.assertEqual(len(cast(object.Array, evaluated).elements), 3)

        self._test_integer_object(cast(object.Array, evaluated).elements[0], 1)
        self._test_integer_object(cast(object.Array, evaluated).elements[1], 4)
        self._test_integer_object(cast(object.Array, evaluated).elements[2], 6)

    def test_array_index_expressions(self) -> None:
        tests = [
            ("[1, 2, 3][0]", 1),
            ("[1, 2, 3][1]", 2),
            ("[1, 2, 3][2]", 3),
            ("let i = 0; [1][i];", 1),
            ("[1, 2, 3][1 + 1];", 3),
            ("let myArray = [1, 2, 3]; myArray[2];", 3),
            ("let myArray = [1, 2, 3]; myArray[0] + myArray[1] + myArray[2];", 6),
            ("let myArray = [1, 2, 3]; let i = myArray[0]; myArray[i]", 2),
            ("[1, 2, 3][3]", None),
            ("[1, 2, 3][-1]", None),
        ]

        for tt in tests:
            evaluated = self._test_eval(tt[0])

            if isinstance(tt[1], int):
                self._test_integer_object(evaluated, tt[1])
            else:
                self._test_null_object(evaluated)

    def test_hash_literals(self) -> None:
        input = """
        let two = "two";
        {
            "one": 10 - 9,
            two: 1 + 1,
            "thr" + "ee": 6 / 2,
            4: 4,
            true: 5,
            false: 6
        }
        """

        evaluated = self._test_eval(input)

        self.assertIsInstance(evaluated, object.Hash)

        expected: Dict[object.HashKey, int] = {
            object.String("one").hash_key(): 1,
            object.String("two").hash_key(): 2,
            object.String("three").hash_key(): 3,
            object.Integer(4).hash_key(): 4,
            object.Boolean(True).hash_key(): 5,
            object.Boolean(False).hash_key(): 6,
        }

        self.assertEqual(len(cast(object.Hash, evaluated).pairs), len(expected))

        for expected_key, expected_value in expected.items():
            pair = cast(object.Hash, evaluated).pairs[expected_key]
            self._test_integer_object(pair.value, expected_value)

    def test_hash_index_expressions(self) -> None:
        tests = [
            ('{"foo": 5}["foo"]', 5),
            ('{"foo": 5}["bar"]', None),
            ('let key = "foo"; {"foo": 5}[key]', 5),
            ('{}["foo"]', None),
            ("{5: 5}[5]", 5),
            ("{true: 5}[true]", 5),
            ("{false: 5}[false]", 5),
        ]

        for tt in tests:
            evaluated = self._test_eval(tt[0])

            if isinstance(tt[1], int):
                self._test_integer_object(evaluated, tt[1])
            else:
                self._test_null_object(evaluated)

    def _test_null_object(self, obj: object.Object) -> None:
        self.assertEqual(obj, Eval.null)

    def _test_eval(self, input: str) -> object.Object:
        lexer = Lexer(input)
        parser = Parser(lexer)
        program = parser.parse_program()
        env = Environment.new_environment()
        eval = Eval()

        evaluated = eval.eval(program, env)
        self.assertNotEqual(evaluated, None)

        return evaluated

    def _test_integer_object(self, obj: object.Object, expected: int) -> None:
        self.assertIsInstance(obj, object.Integer)
        self.assertEqual(cast(object.Integer, obj).value, expected)

    def _test_boolean_object(self, obj: object.Object, expected: bool) -> None:
        self.assertIsInstance(obj, object.Boolean)
        self.assertEqual(cast(object.Boolean, obj).value, expected)
