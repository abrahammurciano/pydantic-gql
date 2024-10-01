from io import StringIO
from typing import Iterable, override

from ..gql_field import GqlField
from .args_builder import ArgsBuilder
from .builder import Builder
from .indentation import Indentation


class FieldsBuilder(Builder[Iterable[GqlField]]):
    """A GraphQL fields builder.

    This class is used to convert a sequence of `GqlField` objects into a string containing the GraphQL fields code.
    """

    def __init__(self, indentation: Indentation) -> None:
        self._indentation = indentation

    @override
    def insert(self, fields: Iterable[GqlField], buffer: StringIO) -> None:
        """Convert a sequence of `GqlField` objects into a GraphQL fields string.

        Args:
            fields: The fields to convert.

        Returns:
            The fields as a string.
        """
        for field in fields:
            self._insert_field(field, buffer)

    def _insert_field(self, field: GqlField, buffer: StringIO) -> None:
        """Insert one field into the resulting string buffer."""
        buffer.write(f"{self._indentation}{field.name}")
        if field.args:
            ArgsBuilder().insert(field.args, buffer)
        if field.fields:
            buffer.write(" {")
            FieldsBuilder(self._indentation + 1).insert(field.fields, buffer)
            buffer.write(str(self._indentation))
            buffer.write("}")
        buffer.write(",")
