from typing import Generic, Mapping, Self, TypeVar, overload

from .base_vars import BaseVars

T = TypeVar("T")


class Var(Generic[T]):
    def __init__(
        self,
        name: str | None = None,
        default: T | None = None,
        type: type[T] | None = None,
    ):
        self.default = default
        self._type = type
        self._name = name

    @property
    def name(self) -> str:
        """The name of the variable."""
        assert self._name is not None, "Var name is not set"
        return self._name

    @property
    def var_type(self) -> type[T]:
        """The python type of the variable."""
        assert self._type is not None, "Var type is not set"
        return self._type

    @property
    def type_name(self) -> str:
        """The GraphQL type of the variable as a string."""
        type_map: Mapping[type, str] = {
            str: "String",
            int: "Int",
            float: "Float",
            bool: "Boolean",
        }
        try:
            return type_map[self.var_type] + ("!" if self.default is None else "")
        except KeyError:
            raise ValueError(f"Cannot convert type {self.var_type} to GraphQL type.")

    @overload
    def __get__(self, instance: None, owner: type) -> Self: ...
    @overload
    def __get__(self, instance: BaseVars, owner: type) -> T: ...
    def __get__(self, instance: BaseVars | None, owner: type) -> T | Self:
        if instance is None:
            return self
        return instance.__values__[self.name]

    def __set__(self, instance: BaseVars, value: T) -> None:
        instance.__values__[self.name] = value

    def __repr__(self) -> str:
        return f"Var(name={self._name or '...'}, type={self._type.__qualname__ if self._type else '...'}, default={self.default})"

    def __str__(self) -> str:
        return f"${self.name}"
