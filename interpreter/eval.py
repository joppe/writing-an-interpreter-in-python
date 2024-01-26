from typing import List, cast
from interpreter import ast
from interpreter import object
from interpreter import environment


class Eval:
    null = object.Null()
    true = object.Boolean(True)
    false = object.Boolean(False)

    def eval(self, node: ast.Node, env: environment.Environment) -> object.Object:
        if isinstance(node, ast.Program):
            return self._eval_program(node, env)

        if isinstance(node, ast.ExpressionStatement):
            return self.eval(node.expression, env)

        if isinstance(node, ast.PrefixExpression):
            right = self.eval(node.right, env)

            if self._is_error(right):
                return right

            return self._eval_prefix_expression(node.operator, right)

        if isinstance(node, ast.InfixExpression):
            left = self.eval(node.left, env)

            if self._is_error(left):
                return left

            right = self.eval(node.right, env)

            if self._is_error(right):
                return right

            return self._eval_infix_expression(node.operator, left, right)

        if isinstance(node, ast.BlockStatement):
            return self._eval_block_statements(
                cast(List[ast.BlockStatement], node.statements), env
            )

        if isinstance(node, ast.IfExpression):
            return self._eval_if_expression(node, env)

        if isinstance(node, ast.ReturnStatement):
            value = self.eval(node.return_value, env)

            if self._is_error(value):
                return value

            return object.ReturnValue(value)

        if isinstance(node, ast.FunctionLiteral):
            params = node.parameters
            body = node.body

            return object.Function(params, body, env)

        if isinstance(node, ast.CallExpression):
            function = self.eval(node.function, env)

            if self._is_error(function):
                return function

            args = self._eval_expressions(node.arguments, env)

            if len(args) == 1 and self._is_error(args[0]):
                return args[0]

            return self._apply_function(function, args)

        if isinstance(node, ast.LetStatement):
            value = self.eval(node.expression, env)

            if self._is_error(value):
                return value

            return env.set(node.name.value, value)

        if isinstance(node, ast.Identifier):
            return self._eval_identifier(node, env)

        if isinstance(node, ast.IntegerLiteral):
            return object.Integer(node.value)

        if isinstance(node, ast.Boolean):
            return self._native_bool_to_boolean_object(node.value)

        if isinstance(node, ast.StringLiteral):
            return object.String(node.value)

        raise NotImplementedError

    def _apply_function(
        self, fn: object.Object, args: List[object.Object]
    ) -> object.Object:
        if isinstance(fn, object.Function):
            extended_env = self._extend_function_env(fn, args)
            evaluated = self.eval(fn.body, extended_env)

            return self._unwrap_return_value(evaluated)

        return self._new_error(f"not a function: {fn.type().name}")

    def _unwrap_return_value(self, obj: object.Object) -> object.Object:
        if isinstance(obj, object.ReturnValue):
            return obj.value

        return obj

    def _extend_function_env(
        self,
        fn: object.Function,
        args: List[object.Object],
    ) -> environment.Environment:
        env = environment.Environment.new_enclosed_environment(fn.env)

        for index, param in enumerate(fn.parameters):
            env.set(param.value, args[index])

        return env

    def _eval_expressions(
        self, exps: List[ast.Expression], env: environment.Environment
    ) -> List[object.Object]:
        result: List[object.Object] = []

        for exp in exps:
            evaluated = self.eval(exp, env)

            if self._is_error(evaluated):
                return [evaluated]

            result.append(evaluated)

        return result

    def _eval_identifier(
        self, node: ast.Identifier, env: environment.Environment
    ) -> object.Object:
        value = env.get(node.value)

        if value is not None:
            return value

        return self._new_error(f"identifier not found: {node.value}")

    def _new_error(self, message: str) -> object.Error:
        return object.Error(message)

    def _is_error(self, obj: object.Object) -> bool:
        if obj is not None:
            return obj.type() == object.ObjectType.ERROR

        return False

    def _eval_program(
        self, program: ast.Program, env: environment.Environment
    ) -> object.Object:
        result: object.Object = object.Null()

        for statement in program.statements:
            result = self.eval(statement, env)

            if isinstance(result, object.ReturnValue):
                return result.value

            if isinstance(result, object.Error):
                return result

        return result

    def _eval_if_expression(
        self, ie: ast.IfExpression, env: environment.Environment
    ) -> object.Object:
        condition = self.eval(ie.condition, env)

        if self._is_error(condition):
            return condition

        if self._is_truthy(condition):
            return self.eval(ie.consequence, env)

        if ie.alternative is not None:
            return self.eval(ie.alternative, env)

        return Eval.null

    def _is_truthy(self, obj: object.Object) -> bool:
        match obj:
            case Eval.null:
                return False
            case Eval.true:
                return True
            case Eval.false:
                return False
            case _:
                return True

    def _eval_infix_expression(
        self, operator: str, left: object.Object, right: object.Object
    ) -> object.Object:
        if isinstance(left, object.Integer) and isinstance(right, object.Integer):
            return self._eval_integer_infix_expression(operator, left, right)

        if operator == "==":
            return self._native_bool_to_boolean_object(left == right)

        if operator == "!=":
            return self._native_bool_to_boolean_object(left != right)

        if left.type() != right.type():
            return self._new_error(
                f"type mismatch: {left.type().name} {operator} {right.type().name}"
            )

        if isinstance(left, object.String) and isinstance(right, object.String):
            return self._eval_string_infix_expression(operator, left, right)

        return self._new_error(
            f"unknown operator: {left.type().name} {operator} {right.type().name}"
        )

    def _eval_string_infix_expression(
        self, operator: str, left: object.String, right: object.String
    ) -> object.Object:
        if operator != "+":
            return self._new_error(
                f"unknown operator: {left.type().name} {operator} {right.type().name}"
            )

        return object.String(left.value + right.value)

    def _eval_integer_infix_expression(
        self, operator: str, left: object.Integer, right: object.Integer
    ) -> object.Object:
        left_value = left.value
        right_value = right.value

        match operator:
            case "+":
                return object.Integer(left_value + right_value)
            case "-":
                return object.Integer(left_value - right_value)
            case "*":
                return object.Integer(left_value * right_value)
            case "/":
                return object.Integer(left_value // right_value)
            case "<":
                return self._native_bool_to_boolean_object(left_value < right_value)
            case ">":
                return self._native_bool_to_boolean_object(left_value > right_value)
            case "==":
                return self._native_bool_to_boolean_object(left_value == right_value)
            case "!=":
                return self._native_bool_to_boolean_object(left_value != right_value)
            case _:
                return self._new_error(
                    f"unknown operator: {left.type().name} {operator} {right.type().name}"
                )

    def _eval_prefix_expression(
        self, operator: str, right: object.Object
    ) -> object.Object:
        match operator:
            case "!":
                return self._eval_bang_operator_expression(right)
            case "-":
                return self._eval_minus_prefix_operator_expression(right)
            case _:
                return self._new_error(
                    f"unknown operator: {operator}{right.type().name}"
                )

    def _eval_minus_prefix_operator_expression(
        self, right: object.Object
    ) -> object.Object:
        if not isinstance(right, object.Integer):
            return self._new_error(f"unknown operator: -{right.type().name}")

        value = right.value

        return object.Integer(-value)

    def _eval_bang_operator_expression(self, right: object.Object) -> object.Object:
        match right:
            case Eval.true:
                return Eval.false
            case Eval.false:
                return Eval.true
            case Eval.null:
                return Eval.true
            case _:
                return Eval.false

    def _eval_block_statements(
        self, statements: List[ast.BlockStatement], env: environment.Environment
    ) -> object.Object:
        result: object.Object = object.Null()

        for statement in statements:
            result = self.eval(statement, env)

            if result is not None and (
                isinstance(result, object.ReturnValue)
                or isinstance(result, object.Error)
            ):
                return result

        return result

    def _native_bool_to_boolean_object(self, value: bool) -> object.Boolean:
        return Eval.true if value else Eval.false
