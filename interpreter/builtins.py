from typing import Dict, List

from interpreter import object


def len_fn(args: List[object.Object]) -> object.Object:
    if len(args) != 1:
        return object.Error(f"wrong number of arguments. got={len(args)}, want=1")

    if isinstance(args[0], object.String):
        return object.Integer(len(args[0].value))

    if isinstance(args[0], object.Array):
        return object.Integer(len(args[0].elements))

    return object.Error(f"argument to `len` not supported, got {args[0].type()}")


def first_fn(args: List[object.Object]) -> object.Object:
    if len(args) != 1:
        return object.Error(f"wrong number of arguments. got={len(args)}, want=1")

    if not isinstance(args[0], object.Array):
        return object.Error(f"argument to `first` must be ARRAY, got {args[0].type()}")

    arr = args[0]

    if len(arr.elements) > 0:
        return arr.elements[0]

    return object.Null()


def last_fn(args: List[object.Object]) -> object.Object:
    if len(args) != 1:
        return object.Error(f"wrong number of arguments. got={len(args)}, want=1")

    if not isinstance(args[0], object.Array):
        return object.Error(f"argument to `last` must be ARRAY, got {args[0].type()}")

    arr = args[0]

    if len(arr.elements) > 0:
        return arr.elements[-1]

    return object.Null()


def rest_fn(args: List[object.Object]) -> object.Object:
    if len(args) != 1:
        return object.Error(f"wrong number of arguments. got={len(args)}, want=1")

    if not isinstance(args[0], object.Array):
        return object.Error(f"argument to `rest` must be ARRAY, got {args[0].type()}")

    arr = args[0]

    if len(arr.elements) > 0:
        return object.Array(arr.elements[1:])

    return object.Null()


def push_fn(args: List[object.Object]) -> object.Object:
    if len(args) != 2:
        return object.Error(f"wrong number of arguments. got={len(args)}, want=2")

    if not isinstance(args[0], object.Array):
        return object.Error(f"argument to `push` must be ARRAY, got {args[0].type()}")

    arr = args[0]
    new_elements = arr.elements.copy()
    new_elements.append(args[1])

    return object.Array(new_elements)


builtins: Dict[str, object.Builtin] = {
    "len": object.Builtin(len_fn),
    "first": object.Builtin(first_fn),
    "last": object.Builtin(last_fn),
    "rest": object.Builtin(rest_fn),
}
