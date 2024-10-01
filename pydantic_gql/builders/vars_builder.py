from io import StringIO
from typing import Any, Sequence, override

from ..var import Var
from .builder import Builder
from .type_builder import TypeBuilder


class VarsBuilder(Builder[Sequence[Var[Any]]]):
    @override
    def insert(self, variables: Sequence[Var[Any]], buffer: StringIO) -> None:
        """Insert variables into the resulting string buffer."""
        if not variables:
            return
        buffer.write("(")
        type_builder = TypeBuilder()
        buffer.write(
            ", ".join(f"${v.name}: {type_builder.build(v)}" for v in variables)
        )
        buffer.write(")")
