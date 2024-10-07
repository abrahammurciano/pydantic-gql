from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .var import Var


@dataclass
class Expr:
    """An explicit expression for an argument in a GraphQL query.

    Args:
        value: The string representation of the expression in GraphQL.
    """

    value: str

    def __str__(self) -> str:
        return self.value


GqlValue = str | int | float | bool | None | Iterable[Any] | Var[Any] | Expr
