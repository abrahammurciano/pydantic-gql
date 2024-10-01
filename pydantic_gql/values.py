from __future__ import annotations

from typing import Any, Iterable

from .var import Var


class Expr:
    """An explicit expression for an argument in a GraphQL query.

    Args:
        value: The string representation of the expression in GraphQL.
    """

    def __init__(self, value: str) -> None:
        self.value = value

    def __str__(self) -> str:
        return self.value


GqlValue = str | int | float | bool | None | Iterable[Any] | Var[Any] | Expr
