import typing, datetime


class SelectStmt:
    def __init__(
        self,
        from_table: "Identifier",
        condition: "Operation | Operand",
    ):
        self.from_table_name = from_table.name
        self.condition = condition

    def __repr__(self):
        return f"SelectStmt(table_name={repr(self.from_table_name)}, condition={repr(self.condition)})"


class FunctionCall:
    def __init__(self, func_name: str, arguments: "list[Operand]"):
        self.func_name = func_name
        self.arguments = arguments

    def __repr__(self):
        return f"FunctionCall(func_name={repr(self.func_name)}, arguments={repr(self.arguments)})"


class Operation:
    def __init__(self, operator: "Operator", *operands: "Operand"):
        self.operator = operator
        self.operands = list(operands)

    def __repr__(self):
        return (
            f"Operation(operator={repr(self.operator)}, operands={repr(self.operands)})"
        )


class Identifier:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"Identifier(name={repr(self.name)})"


class Value:
    def __init__(self, value: str | int | float | datetime.date | bool | None):
        self.value = value

    def __repr__(self):
        return f"Value(value={repr(self.value)}, type={type(self.value).__name__})"


Operator = (
    typing.Literal["OR"]
    | typing.Literal["AND"]
    | typing.Literal["NOT"]
    | typing.Literal["="]
    | typing.Literal["<>"]
    | typing.Literal["<"]
    | typing.Literal["<="]
    | typing.Literal[">"]
    | typing.Literal[">="]
    | typing.Literal["BETWEEN"]
    | typing.Literal["IN"]
    | typing.Literal["NOT IN"]
    | typing.Literal["LIKE"]
    | typing.Literal["NOT LIKE"]
    | typing.Literal["SLIKE"]
    | typing.Literal["NSLIKE"]
)
Operand = Identifier | Value | FunctionCall
ConditionExpr = Operation | Operand
