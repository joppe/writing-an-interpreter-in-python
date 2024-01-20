from typing import List, cast
from interpreter import ast
from interpreter import object


class Eval:
    null = object.Null()
    true = object.Boolean(True)
    false = object.Boolean(False)

    def eval(self, node: ast.Node) -> object.Object:
        if isinstance(node, ast.Program):
            return self._eval_program(node)

        if isinstance(node, ast.ExpressionStatement):
            return self.eval(node.expression)

        if isinstance(node, ast.PrefixExpression):
            right = self.eval(node.right)

            if self._is_error(right):
                return right

            return self._eval_prefix_expression(node.operator, right)

        if isinstance(node, ast.InfixExpression):
            left = self.eval(node.left)

            if self._is_error(left):
                return left

            right = self.eval(node.right)

            if self._is_error(right):
                return right

            return self._eval_infix_expression(node.operator, left, right)

        if isinstance(node, ast.BlockStatement):
            return self._eval_block_statements(
                cast(List[ast.BlockStatement], node.statements)
            )

        if isinstance(node, ast.IfExpression):
            return self._eval_if_expression(node)

        if isinstance(node, ast.ReturnStatement):
            value = self.eval(node.return_value)

            if self._is_error(value):
                return value

            return object.ReturnValue(value)

        if isinstance(node, ast.IntegerLiteral):
            return object.Integer(node.value)

        if isinstance(node, ast.Boolean):
            return self._native_bool_to_boolean_object(node.value)

        raise NotImplementedError

    def _new_error(self, message: str) -> object.Error:
        return object.Error(message)

    def _is_error(self, obj: object.Object) -> bool:
        if obj is not None:
            return obj.type() == object.ObjectType.ERROR

        return False

    def _eval_program(self, program: ast.Program) -> object.Object:
        result: object.Object = object.Null()

        for statement in program.statements:
            result = self.eval(statement)

            if isinstance(result, object.ReturnValue):
                return result.value

            if isinstance(result, object.Error):
                return result

        return result

    def _eval_if_expression(self, ie: ast.IfExpression) -> object.Object:
        condition = self.eval(ie.condition)

        if self._is_error(condition):
            return condition

        if self._is_truthy(condition):
            return self.eval(ie.consequence)

        if ie.alternative is not None:
            return self.eval(ie.alternative)

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

        return self._new_error(
            f"unknown operator: {left.type().name} {operator} {right.type().name}"
        )

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
        self, statements: List[ast.BlockStatement]
    ) -> object.Object:
        result: object.Object = object.Null()

        for statement in statements:
            result = self.eval(statement)

            if result is not None and (
                isinstance(result, object.ReturnValue)
                or isinstance(result, object.Error)
            ):
                return result

        return result

    def _native_bool_to_boolean_object(self, value: bool) -> object.Boolean:
        return Eval.true if value else Eval.false
