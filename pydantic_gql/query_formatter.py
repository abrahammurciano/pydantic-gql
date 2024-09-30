from io import StringIO
from typing import Any, Iterable, Sequence

from pydantic_gql.gql_field import GqlField
from pydantic_gql.var import Var

from .query import Query


class QueryFormatter:
    """A GraphQL query formatter.

    Args:
        indent: The indentation to use when formatting the output. If `False` then no indentation is used and the query is returned as a single line. If `True` (the default) then the default indentation is used (two spaces). If an integer then that many spaces are used for indentation. If a string (must be whitespace) then that string is used for indentation.
    """

    DEFAULT_INDENTATION = "  "

    def __init__(self, indent: int | str | bool = True) -> None:
        self._should_indent = indent is not False
        if isinstance(indent, bool):
            self._indentation = self.DEFAULT_INDENTATION if indent else ""
        elif isinstance(indent, str):
            if not indent.isspace():
                raise ValueError("indent must be whitespace if it is a string.")
            self._indentation = indent
        else:
            self._indentation = " " * indent

    def format(self, query: Query) -> str:
        """Format a query.

        Args:
            query: The query to format.

        Returns:
            The formatted query.
        """
        result = StringIO()
        result.write(f"query {query.name}")
        self._insert_vars(result, query.variables)
        result.write(" {")
        self._insert_fields(result, query.fields)
        result.write(f"{self._indent(0)}}}")
        return result.getvalue()

    def __call__(self, query: Query) -> str:
        return self.format(query)

    def _insert_vars(self, result: StringIO, variables: Sequence[Var[Any]]) -> None:
        """Insert variables into the resulting string buffer."""
        if not variables:
            return
        result.write("(")
        result.write(", ".join(f"{v}: {v.type_name}" for v in variables))
        result.write(")")

    def _insert_fields(
        self, result: StringIO, fields: Iterable[GqlField], level: int = 1
    ) -> None:
        """Insert fields into the resulting string buffer."""
        for field in fields:
            self._insert_field(result, field, level)

    def _insert_field(self, result: StringIO, field: GqlField, level: int) -> None:
        """Insert one field into the resulting string buffer."""
        result.write(f"{self._indent(level)}{field.name}")
        if field.remote_name:
            result.write(f": {field.remote_name}")
        # TODO: include args
        if field.fields:
            result.write(" {")
            self._insert_fields(result, field.fields, level + 1)
            result.write(f"{self._indent(level)}")
            result.write("}")
        result.write(",")

    def _indent(self, level: int) -> str:
        """Get the indentation string for a given level."""
        return "\n" + self._indentation * level if self._should_indent else ""
