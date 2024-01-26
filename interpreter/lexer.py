from interpreter.token import Token
from interpreter.token_type import TokenType, lookup_ident

EMPTY_CHAR = "\u0000"
WHITESPACE = {" ", "\t", "\n", "\r"}


class Lexer:
    def __init__(self, input: str) -> None:
        self._input = input
        self._position = 0
        self._read_position = 0
        self._char = EMPTY_CHAR

        self._read_char()

    def next_token(self) -> Token:
        self._skip_whitespace()

        match self._char:
            case "=":
                if self.peek_char() == "=":
                    self._read_char()

                    token = Token(TokenType.EQ, "==")
                else:
                    token = Token(TokenType.ASSIGN, self._char)
            case "+":
                token = Token(TokenType.PLUS, self._char)
            case "-":
                token = Token(TokenType.MINUS, self._char)
            case "!":
                if self.peek_char() == "=":
                    self._read_char()

                    token = Token(TokenType.NOT_EQ, "!=")
                else:
                    token = Token(TokenType.BANG, self._char)
            case "/":
                token = Token(TokenType.SLASH, self._char)
            case "*":
                token = Token(TokenType.ASTERISK, self._char)
            case "<":
                token = Token(TokenType.LT, self._char)
            case ">":
                token = Token(TokenType.GT, self._char)
            case ";":
                token = Token(TokenType.SEMICOLON, self._char)
            case "(":
                token = Token(TokenType.LPAREN, self._char)
            case ")":
                token = Token(TokenType.RPAREN, self._char)
            case ",":
                token = Token(TokenType.COMMA, self._char)
            case "{":
                token = Token(TokenType.LBRACE, self._char)
            case "}":
                token = Token(TokenType.RBRACE, self._char)
            case '"':
                token = Token(TokenType.STRING, self._read_string())
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
                    token = Token(TokenType.ILLEGAL, self._char)

        self._read_char()

        return token

    def peek_char(self) -> str:
        if self._read_position >= len(self._input):
            return EMPTY_CHAR

        return self._input[self._read_position]

    def _read_string(self) -> str:
        position = self._position + 1

        while True:
            self._read_char()

            if self._char == '"' or self._char == EMPTY_CHAR:
                break

        return self._input[position : self._position]

    def _read_identifier(self) -> str:
        position = self._position

        while self._is_letter():
            self._read_char()

        return self._input[position : self._position]

    def _read_number(self) -> str:
        position = self._position

        while self._is_digit():
            self._read_char()

        return self._input[position : self._position]

    def _read_char(self):
        if self._read_position >= len(self._input):
            self._char = EMPTY_CHAR
        else:
            self._char = self._input[self._read_position]

        self._position = self._read_position
        self._read_position += 1

    def _is_letter(self) -> bool:
        return self._char.isalpha() or self._char == "_"

    def _is_digit(self) -> bool:
        return self._char.isdigit()

    def _skip_whitespace(self):
        while self._char in WHITESPACE:
            self._read_char()

    def __iter__(self):
        token = self.next_token()

        while token.token_type != TokenType.EOF:
            yield token

            token = self.next_token()

        yield token
