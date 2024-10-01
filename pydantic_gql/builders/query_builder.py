from io import StringIO
from typing import override

from ..query import Query
from .builder import Builder
from .fields_builder import FieldsBuilder
from .indentation import Indentation
from .vars_builder import VarsBuilder


class QueryBuilder(Builder[Query]):
    """A GraphQL query builder.

    This class is used to convert a `Query` object into a string containing the GraphQL query code.

    Args:
        indent: The indentation to use when formatting the output. If `False` then no indentation is used and the query is returned as a single line. If `True` (the default) then the default indentation is used (two spaces). If an integer then that many spaces are used for indentation. If a string (must be whitespace) then that string is used for indentation.
    """

    DEFAULT_INDENTATION = "  "

    def __init__(self, indent: int | str | bool = True) -> None:
        indentation: str | None
        if isinstance(indent, bool):
            indentation = self.DEFAULT_INDENTATION if indent else None
        elif isinstance(indent, str):
            if not indent.isspace():
                raise ValueError("indent must be whitespace if it is a string.")
            indentation = indent
        else:
            indentation = " " * indent
        self._indentation = Indentation(indentation, 0)

    @override
    def insert(self, query: Query, buffer: StringIO) -> None:
        """Convert a `Query` object into a GraphQL query string.

        Args:
            query: The query to convert.

        Returns:
            The query as a string.
        """
        buffer.write(f"query {query.name}")
        VarsBuilder().insert(query.variables, buffer)
        buffer.write(" {")
        FieldsBuilder(self._indentation + 1).insert(query.fields, buffer)
        buffer.write(str(self._indentation))
        buffer.write("}")
