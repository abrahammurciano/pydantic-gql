from __future__ import annotations

from functools import cached_property
from types import UnionType
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Self,
    TypeVar,
    Union,
    cast,
    get_args,
    get_origin,
    overload,
)

if TYPE_CHECKING:
    from .base_vars import BaseVars

T = TypeVar("T")


NOTSET: Any = object()


class Var(Generic[T]):
    """A variable definition for a GraphQL query.

    Args:
        name: The name of the variable. If used as a class attribute on a `BaseVars` subclass, the name will be extracted from the attribute name if not provided.
        default: The default value of the variable. If the type annotation allows `None`, the default value will be `None` if not provided. Otherwise, the variable will be considered required.
        type: The python type of the variable. If used as a class attribute on a `BaseVars` subclass, the type will be extracted from the type annotation if not provided. It can also be extracted from the type annotation used when creating the `Var` instance, e.g. `Var[str]("name")`.
    """

    def __init__(
        self,
        name: str | None = None,
        default: T = NOTSET,
        type: type[T] | None = None,
    ):
        self._default = default
        self._type = type
        self._name = name

    @property
    def name(self) -> str:
        """The name of the variable."""
        assert self._name is not None, "Var name is not set"
        return self._name

    @cached_property
    def var_type(self) -> type[T]:
        """The python type of the variable."""
        if self._type:
            return self._type
        if hasattr(self, "__orig_class__"):
            args = get_args(getattr(self, "__orig_class__"))
            if len(args) == 1:
                return args[0]
        raise ValueError("Var type is not set")

    @cached_property
    def required(self) -> bool:
        """Whether the variable is required.

        A variable is required if (1) no default value is set *and* (2) the type annotation does not allow None.
        """
        if self._default is not NOTSET:
            return False
        return is_required(self.var_type)

    @property
    def default(self) -> T:
        """The default value of the variable.

        If the variable is required, accessing this property will raise a `ValueError`.
        """
        if not self.required and self._default is NOTSET:
            return cast(T, None)
        if self.required:
            raise ValueError("No default value set")
        return self._default

    def set_default_name(self, name: str) -> None:
        """Set the name of the variable if it is not set."""
        if self._name is None:
            self._name = name

    def set_default_type(self, var_type: type[T]) -> None:
        """Set the type of the variable if it is not set."""
        if self._type is None:
            self._type = var_type
            self.__dict__.pop("var_type", None)
            self.__dict__.pop("required", None)

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
        return f"<Var {self._name or '...'}: {getattr(self._type, '__qualname__', self._type or '...')} {'required' if self.required else f'= {self.default}'}>"


def is_required(t: type | UnionType) -> bool:
    """Check if a type annotation is required."""
    return get_origin(t) not in (Union, UnionType) or all(
        arg is not type(None) for arg in get_args(t)
    )
