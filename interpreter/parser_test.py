import unittest
from interpreter.ast import LetStatement
from interpreter.lexer import Lexer
from interpreter.parser import Parser


class TestParser(unittest.TestCase):
    def test_let_statements(self):
        input = """
            let x = 5;
            let y = 10;
            let foobar = 838383;
        """
        lexer = Lexer(input)
        parser = Parser(lexer)
        program = parser.parse_program()

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

        parser_errors = parser.errors()

        if len(parser_errors) != 0:
            for error in parser_errors:
                print(f"parser error: {error}")

        self.assertEqual(len(parser_errors), 0)
