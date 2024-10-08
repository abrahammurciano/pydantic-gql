from io import StringIO
from typing import override

from ..operation import Operation
from .builder import Builder
from .fields_builder import FieldsBuilder
from .indentation import Indentation
from .vars_builder import VarsBuilder


class OperationBuilder(Builder[Operation]):
    """A GraphQL operation builder.

    This class is used to convert an `Operation` object into a string containing the GraphQL code.

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
    def insert(self, operation: Operation, buffer: StringIO) -> None:
        """Insert the operation as a string of GraphQL code into the buffer.

        Args:
            operation: The operation to convert to a string and insert into the buffer.
            buffer: The buffer to write the operation to.
        """
        buffer.write(f"{operation.type} {operation.name}")
        VarsBuilder().insert(operation.variables, buffer)
        buffer.write(" {")
        FieldsBuilder(self._indentation + 1).insert(operation.fields, buffer)
        buffer.write(str(self._indentation))
        buffer.write("}")
