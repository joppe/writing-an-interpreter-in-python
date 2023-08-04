from interpreter.token_type import TokenType


class Token:
    def __init__(self, token_type: TokenType, literal: str):
        self.token_type = token_type
        self.literal = literal

    def __repr__(self) -> str:
        return f"Token({self.token_type}, {self.literal})"
