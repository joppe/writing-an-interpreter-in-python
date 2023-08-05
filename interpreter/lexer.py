from interpreter.token import Token
from interpreter.token_type import TokenType, lookup_ident

EMPTY_CHAR = "\u0000"
WHITESPACE = {" ", "\t", "\n", "\r"}


class Lexer:
    def __init__(self, input: str):
        self.input = input
        self.position = 0
        self.read_position = 0
        self.char = EMPTY_CHAR

        self._read_char()

    def next_token(self) -> Token:
        self._skip_whitespace()

        match self.char:
            case "=":
                if self.peek_char() == "=":
                    self._read_char()

                    token = Token(TokenType.EQ, "==")
                else:
                    token = Token(TokenType.ASSIGN, self.char)
            case "+":
                token = Token(TokenType.PLUS, self.char)
            case "-":
                token = Token(TokenType.MINUS, self.char)
            case "!":
                if self.peek_char() == "=":
                    self._read_char()

                    token = Token(TokenType.NOT_EQ, "!=")
                else:
                    token = Token(TokenType.BANG, self.char)
            case "/":
                token = Token(TokenType.SLASH, self.char)
            case "*":
                token = Token(TokenType.ASTERISK, self.char)
            case "<":
                token = Token(TokenType.LT, self.char)
            case ">":
                token = Token(TokenType.GT, self.char)
            case ";":
                token = Token(TokenType.SEMICOLON, self.char)
            case "(":
                token = Token(TokenType.LPAREN, self.char)
            case ")":
                token = Token(TokenType.RPAREN, self.char)
            case ",":
                token = Token(TokenType.COMMA, self.char)
            case "{":
                token = Token(TokenType.LBRACE, self.char)
            case "}":
                token = Token(TokenType.RBRACE, self.char)
            case "\u0000":
                token = Token(TokenType.EOF, "")
            case _:
                if self._is_letter():
                    identifier = self._read_identifier()
                    token_type = lookup_ident(identifier)
                    token = Token(token_type, identifier)

                    return token
                elif self._is_digit():
                    number = self._read_number()
                    token = Token(TokenType.INT, number)

                    return token
                else:
                    token = Token(TokenType.ILLEGAL, self.char)

        self._read_char()

        return token

    def peek_char(self) -> str:
        if self.read_position >= len(self.input):
            return EMPTY_CHAR

        return self.input[self.read_position]

    def _read_identifier(self) -> str:
        position = self.position

        while self._is_letter():
            self._read_char()

        return self.input[position : self.position]

    def _read_number(self) -> str:
        position = self.position

        while self._is_digit():
            self._read_char()

        return self.input[position : self.position]

    def _read_char(self):
        if self.read_position >= len(self.input):
            self.char = EMPTY_CHAR
        else:
            self.char = self.input[self.read_position]

        self.position = self.read_position
        self.read_position += 1

    def _is_letter(self) -> bool:
        return self.char.isalpha() or self.char == "_"

    def _is_digit(self) -> bool:
        return self.char.isdigit()

    def _skip_whitespace(self):
        while self.char in WHITESPACE:
            self._read_char()

    def __iter__(self):
        token = self.next_token()

        while token.token_type != TokenType.EOF:
            yield token

            token = self.next_token()

        yield token
