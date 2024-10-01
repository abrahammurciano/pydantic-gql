from io import StringIO
from typing import Mapping, override

from ..values import GqlValue
from .builder import Builder
from .value_builder import ValueBuilder


class ArgsBuilder(Builder[Mapping[str, GqlValue]]):
    """A GraphQL arguments builder.

    This class is used to convert a mapping of argument names to `GqlValue` objects into a string containing the GraphQL arguments code.
    """

    @override
    def insert(self, args: Mapping[str, GqlValue], buffer: StringIO) -> None:
        """Convert a mapping of argument names to `GqlValue` objects into a GraphQL arguments string.

        Args:
            args: The arguments to convert.

        Returns:
            The arguments as a string.
        """
        buffer.write("(")
        value_builder = ValueBuilder()
        buffer.write(", ".join(f"{k}: {value_builder(v)}" for k, v in args.items()))
        buffer.write(")")
