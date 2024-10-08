from __future__ import annotations

from typing import Any, Iterable

from .gql_field import GqlField
from .var import Var


class Operation:
    """A GraphQL operation object, such as a query or mutation, which is a collection of fields to be queried from a GraphQL API.

    Args:
        op_type: The type of operation, such as "query" or "mutation".
        op_name: The name of the operation. This has no meaning in the GraphQL operation itself; it is just a label for you to identify the operation.
        fields: The fields to include in the operation. These can be created manually or using the `GqlField.from_model` constructor.
        variables: The variables to include in the operation.
    """

    def __init__(
        self,
        op_type: str,
        op_name: str,
        *fields: GqlField,
        variables: Iterable[Var[Any]] = (),
    ) -> None:
        self.type = op_type
        self.name = op_name
        self.fields = fields
        self.variables = tuple(variables)

    def __format__(self, format_spec: str) -> str:
        from .builders.operation_builder import OperationBuilder

        indent: bool | int | str
        if format_spec in ("", "indent"):
            indent = True
        elif format_spec == "noindent":
            indent = False
        elif format_spec.isdigit():
            indent = int(format_spec)
        elif format_spec.isspace():
            indent = format_spec
        else:
            raise ValueError(
                f"Invalid format specifier: {format_spec!r}. Must be one of '', 'indent', 'noindent', whitespace, or a positive integer."
            )
        return OperationBuilder(indent=indent).build(self)

    def __str__(self) -> str:
        return self.__format__("")

    def __repr__(self) -> str:
        return f"<{self.type} {self:noindent}>"
