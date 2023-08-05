import os

from interpreter.repl import repl


def main():
    user = os.getlogin()
    print(f"Hello {user}! This is the Monkey programming language!")
    print("Feel free to type in commands")

    repl()


if __name__ == "__main__":
    main()
