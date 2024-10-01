from io import StringIO
from types import UnionType
from typing import Any, Iterable, Mapping, Union, get_args, get_origin, override

from ..var import Var, is_required
from .builder import Builder


class TypeBuilder(Builder[Var[Any]]):
    @override
    def insert(self, var: Var[Any], buffer: StringIO) -> None:
        """Insert a type into the resulting string buffer."""
        buffer.write(self._type_of(var.var_type, var.required))

    _basic_types: Mapping[type, str] = {
        str: "String",
        int: "Int",
        float: "Float",
        bool: "Boolean",
    }

    def _type_of(self, t: type, required: bool | None = None) -> str:
        """The GraphQL type of the variable as a string."""
        if t in self._basic_types:
            var_type = self._basic_types[t]
        elif self._is_union(t):
            var_type = self._union_type(t)
        elif self._is_iterable(t):
            var_type = self._iterable_type(t)
        else:
            raise ValueError(f"Cannot convert type {t} to GraphQL type.")
        if required is None:
            required = is_required(t)
        return var_type + ("!" if required else "")

    def _is_union(self, t: type) -> bool:
        """Check if a type is a Union."""
        return get_origin(t) in (Union, UnionType)

    def _union_type(self, t: type) -> str:
        """Get the GraphQL type of an Optional or Union type."""
        args = get_args(t)
        if len(args) > 2 or type(None) not in args:
            raise ValueError(f"Only unions with None are supported. Got {t}.")
        return self._type_of(
            next(t for t in args if t is not type(None)), required=False
        )

    def _is_iterable(self, t: type) -> bool:
        """Check if a type is an Iterable."""
        return issubclass(get_origin(t) or t, Iterable)

    def _iterable_type(self, t: type) -> str:
        """Get the GraphQL type of an Iterable."""
        args = get_args(t)
        if len(args) != 1:
            raise ValueError(f"Only iterables with one type are supported. Got {t}.")
        return f"[{self._type_of(args[0])}]"
