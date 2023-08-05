from interpreter.lexer import Lexer


PROMPT = ">>> "


def repl():
    while True:
        try:
            text = input(PROMPT)
        except KeyboardInterrupt:
            break

        if text:
            lexer = Lexer(text)

            for token in lexer:
                print(token)
