from .sql_ast import *

import lark, re

sql_grammar = r"""
    start: select_stmt

    select_stmt: "SELECT" "*" "FROM" identifier "WHERE" condition ";"?

    condition: or_expr

    ?or_expr: and_expr
        | or_expr "OR" and_expr   -> or_op

    ?and_expr: not_expr
        | and_expr "AND" not_expr -> and_op

    ?not_expr: comparison_expr
        | "NOT" not_expr          -> not_op

    ?comparison_expr: operand BINARY_COMP_OPERATOR operand -> binary_comp_op
        | operand "BETWEEN" operand "AND" operand -> between_op
        | operand

    BINARY_COMP_OPERATOR: "=" | "<>" | "<" | ">" | "<=" | ">=" | "LIKE" | "NOT LIKE" | "IN" | "NOT IN" | "IS"

    ?operand: identifier
        | value
        | function_call
        | "(" or_expr ")"

    identifier: IDENTIFIER

    value: STRING | NUMBER | REAL | DATE | BOOL | NULL

    function_call: IDENTIFIER "(" [value ("," value)*] ")"

    IDENTIFIER: /(?!TRUE|FALSE|NULL)[a-zA-Z_][a-zA-Z0-9_]*/
    STRING: /'[^']*'/
    NUMBER: /\d+/
    REAL: /\d+\.\d+/
    DATE: /\d{4}-\d{2}-\d{2}/
    BOOL: "TRUE" | "FALSE"
    NULL: "NULL"

    %import common.WS
    %ignore WS
"""


@lark.v_args(inline=True)
class SQLTransformer(lark.Transformer):
    def start(self, select_stmt: SelectStmt) -> SelectStmt:
        return select_stmt

    def select_stmt(
        self,
        from_table: Identifier,
        condition: Operation | Operand,
    ) -> SelectStmt:
        return SelectStmt(from_table=from_table, condition=condition)

    def condition(self, condition: ConditionExpr) -> ConditionExpr:
        return condition

    def or_op(
        self,
        left: Operation | Operand,
        right: Operation | Operand,
    ) -> Operation:
        return Operation("OR", left, right)

    def and_op(
        self,
        left: Operation | Operand,
        right: Operation | Operand,
    ) -> Operation:
        return Operation("AND", left, right)

    def not_op(self, operand: Operation | Operand) -> Operation:
        return Operation("NOT", operand)

    def binary_comp_op(
        self, left: Operand, operator: lark.Token, right: Operand
    ) -> Operation:
        operator_str = str(operator)
        if operator_str == "IS":
            operator_str = "="
        elif operator_str == "IS NOT":
            operator_str = "<>"
        return Operation(operator_str, left, right)

    def between_op(
        self,
        operand: Operand,
        lower: Operand,
        upper: Operand,
    ) -> Operation:
        return Operation("BETWEEN", operand, lower, upper)

    def operand(self, operand: Operand) -> Operand:
        return operand

    def identifier(self, value: lark.Token) -> Identifier:
        return Identifier(str(value))

    def value(self, value: lark.Token) -> Value:
        value_str = str(value)
        if re.match(r"^\d+$", value_str):
            return Value(int(value_str))
        elif re.match(r"^\d+\.\d+$", value_str):
            return Value(float(value_str))
        elif re.match(r"^\d{4}-\d{2}-\d{2}$", value_str):
            return Value(datetime.datetime.strptime(value_str, r"%Y-%m-%d").date())
        elif value_str.startswith("'") and value_str.endswith("'"):
            return Value(value_str[1:-1])
        elif re.match(r"^(TRUE|FALSE)$", value_str, re.IGNORECASE):
            return Value(value_str.upper() == "TRUE")
        elif re.match(r"^NULL$", value_str, re.IGNORECASE):
            return Value(None)
        else:
            raise ValueError(f"Unable to process value: {repr(value_str)}")

    def function_call(
        self,
        func_name: lark.Token,
        *arguments: Operand,
    ) -> FunctionCall:
        return FunctionCall(str(func_name), list(arguments))


sql_parser = lark.Lark(sql_grammar, parser="lalr", transformer=SQLTransformer())


def parse(sql_code: str) -> SelectStmt:
    return sql_parser.parse(sql_code)
