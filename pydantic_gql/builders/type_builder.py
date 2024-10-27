from io import StringIO
from types import UnionType
from typing import Any, Iterable, Mapping, Union, cast, get_args, get_origin, override

from ..var import TypeAnnotation, Var, is_required
from .builder import Builder


class TypeBuilder(Builder[Var[Any]]):
    @override
    def insert(self, var: Var[Any], buffer: StringIO) -> None:
        """Insert a type into the resulting string buffer."""
        buffer.write(self._type_of(var.var_type, var.required, var.type_name))

    _basic_types: Mapping[TypeAnnotation, str] = {
        str: "String",
        int: "Int",
        float: "Float",
        bool: "Boolean",
    }

    def _type_of(
        self,
        t: TypeAnnotation,
        required: bool | None,
        type_name: str | None,
    ) -> str:
        """The GraphQL type of the variable as a string."""
        if self._is_optional(t):
            var_type = self._optional_type(t, type_name)
        elif self._is_iterable(t):
            var_type = self._iterable_type(t, type_name)
        elif type_name:
            var_type = type_name
        elif t in self._basic_types:
            var_type = self._basic_types[t]
        elif isinstance(t, type):
            var_type = t.__name__
        else:
            raise ValueError(f"Unsupported type: {t}")
        if required is None:
            required = is_required(t)
        return var_type + ("!" if required else "")

    def _is_optional(self, t: TypeAnnotation) -> bool:
        """Check if a type is an optional."""
        args = get_args(t)
        return (
            get_origin(t) in (Union, UnionType)
            and len(args) == 2
            and type(None) in args
        )

    def _optional_type(self, t: TypeAnnotation, type_name: str | None) -> str:
        """Get the GraphQL type of an Optional type."""
        return self._type_of(
            next(t for t in get_args(t) if t is not type(None)),
            required=False,
            type_name=type_name,
        )

    def _is_iterable(self, t: TypeAnnotation) -> bool:
        """Check if a type is an Iterable of any specific type."""
        try:
            return (
                issubclass(cast(Any, get_origin(t) or t), Iterable)
                and len(get_args(t)) == 1
            )
        except TypeError:
            return False

    def _iterable_type(self, t: TypeAnnotation, type_name: str | None) -> str:
        """Get the GraphQL type of an Iterable."""
        return f"[{self._type_of(get_args(t)[0], required=None, type_name=type_name)}]"
