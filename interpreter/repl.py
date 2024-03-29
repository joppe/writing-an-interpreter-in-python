from interpreter.eval import Eval
from interpreter.environment import Environment
from interpreter.lexer import Lexer
from interpreter.parser import Parser


PROMPT = ">>> "


def repl() -> None:
    env = Environment.new_environment()

    while True:
        try:
            text = input(PROMPT)
        except KeyboardInterrupt:
            break

        if text:
            lexer = Lexer(text)
            parser = Parser(lexer)
            program = parser.parse_program()

            parser_errors = parser.errors()

            if len(parser_errors) != 0:
                for error in parser_errors:
                    print(f"parser error: {error}")

                continue

            eval = Eval()
            evaluated = eval.eval(program, env)

            if evaluated is not None:
                print(f"{evaluated.inspect()}")
