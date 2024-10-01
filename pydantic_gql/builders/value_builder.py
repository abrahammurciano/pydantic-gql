import json
from io import StringIO
from typing import Iterable, override

from ..values import GqlValue
from ..var import Var
from .builder import Builder


class ValueBuilder(Builder[GqlValue]):
    """A GraphQL value builder.

    This class is used to convert a `GqlValue` object into a string containing the GraphQL value code.
    """

    @override
    def insert(self, value: GqlValue, buffer: StringIO) -> None:
        """Convert a `GqlValue` object into a GraphQL value string.

        Args:
            value: The value to convert.

        Returns:
            The value as a string.
        """
        if isinstance(value, Var):
            buffer.write(f"${value.name}")
        elif isinstance(value, str):
            buffer.write(json.dumps(value))
        elif isinstance(value, bool):
            buffer.write(str(value).lower())
        elif value is None:
            buffer.write("null")
        elif isinstance(value, Iterable):
            buffer.write(f"[{', '.join(self.build(v) for v in value)}]")
        else:
            buffer.write(str(value))
