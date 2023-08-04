import unittest

from interpreter.token_type import TokenType
from interpreter.token import Token


class TestToken(unittest.TestCase):
    def test_to_string(self):
        token = Token(TokenType.LBRACE, "{")

        self.assertEqual(str(token), "Token(TokenType.LBRACE, {)")


if __name__ == "__main__":
    unittest.main()
