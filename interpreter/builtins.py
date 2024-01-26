from typing import Dict, List

from interpreter import object


def len_fn(args: List[object.Object]) -> object.Object:
    if len(args) != 1:
        return object.Error(f"wrong number of arguments. got={len(args)}, want=1")

    if isinstance(args[0], object.String):
        return object.Integer(len(args[0].value))

    return object.Error(f"argument to `len` not supported, got {args[0].type()}")


builtins: Dict[str, object.Builtin] = {
    "len": object.Builtin(len_fn),
}
