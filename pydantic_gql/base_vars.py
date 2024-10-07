from __future__ import annotations

from abc import ABCMeta
from typing import (
    Any,
    ClassVar,
    Iterator,
    Mapping,
    cast,
    dataclass_transform,
    get_origin,
    get_type_hints,
)

from .var import NOTSET, Var


def _is_var(annotation: Any) -> bool:
    """Check if a type annotation (from typing.get_type_hints) is a `Var`."""
    origin = get_origin(annotation)
    return origin is not ClassVar and issubclass(origin or annotation, Var)


@dataclass_transform(eq_default=False, field_specifiers=(Var,), kw_only_default=True)
class BaseVarsMeta(ABCMeta):
    # Can't actually inherit from Iterable. https://discuss.python.org/t/abcmeta-change-isinstancecheck-of-additional-parent-class/19908
    def __iter__(self) -> Iterator[Var[Any]]:
        return iter(cast(type[BaseVars], self).__variables__.values())


class BaseVars(Mapping[str, Any], metaclass=BaseVarsMeta):
    """Base class for classes that define a set of variables for a GraphQL query.

    # Usage

    To define a set of variables, subclass `BaseVars` and define class attributes with type hints of `Var[T]` where `T` is the type of the variable. Optionally, you can assign an instance of `Var` to provide a default value or to override the name and type of the variable.

    If no `Var` instance is assigned, then the variable name will be extracted from the class attribute name, the variable type will be extracted from the type hint, and the default will be `None` if the type hint allows it (e.g. `Optional[T]` or `T | None`). If the type hint does not allow `None`, then the variable will be required and an error will be raised if it is not provided.

    If a `Var` instance is assigned, it may specify a default value for the variable with the keyword argument `default`. If the keyword argument `name` is provided, it will override the variable name. This is useful for variables that have a different name in the GraphQL query than in the Python code, e.g. `local_name: Var[str] = Var(name="remoteName")` will be treated as `remoteName` in the GraphQL query but as an attribute `local_name` in the Python code.

    ```python
    from pydantic_gql import BaseVars, Var

    class MyVars(BaseVars):
        id: Var[int]
        optional: Var[str | None]
        default: Var[str] = Var(default="default value")
        local_name: Var[str] = Var(name="remoteName")
        many: Var[list[str]]
    ```

    The `MyVars` class is itself an iterable of `Var`s. Instances of `MyVars` have values and is a mapping from variable name to value.
    """

    __variables__: ClassVar[Mapping[str, Var[Any]]]

    def __init_subclass__(cls) -> None:
        cls.__variables__ = {}
        for key, annotation in get_type_hints(cls).items():
            if not _is_var(annotation):
                continue
            value = getattr(cls, key, NOTSET)
            if isinstance(value, Var):
                value.set_default_name(key)
                value.set_default_type(annotation.__args__[0])
                cls.__variables__[key] = value
            else:
                cls.__variables__[key] = Var(key, value, annotation.__args__[0])
        for key, var in cls.__variables__.items():
            setattr(cls, key, var)

    def __init__(self, *args: object, **kwargs: Any) -> None:
        if args:
            raise TypeError(f"{type(self).__name__} takes no positional arguments")
        self.__values__ = {
            var.name: _get_value(key, kwargs, var)
            for key, var in self.__variables__.items()
        }

    def __iter__(self) -> Iterator[str]:
        return iter(self.__values__)

    def __getitem__(self, name: str, /) -> Any:
        return self.__values__[name]

    def __len__(self) -> int:
        return len(self.__values__)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({', '.join(f'{k}={v!r}' for k, v in self.__values__.items())})"


def _get_value(key: str, kwargs: Mapping[str, Any], var: Var[Any]) -> Any:
    if key in kwargs:
        return kwargs[key]
    try:
        return var.default
    except ValueError:
        raise TypeError(f"missing required variable {key!r}") from None
