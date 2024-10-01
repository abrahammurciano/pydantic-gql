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


def _get_value(key: str, kwargs: Mapping[str, Any], var: Var[Any]) -> Any:
    if key in kwargs:
        return kwargs[key]
    try:
        return var.default
    except ValueError:
        raise TypeError(f"missing required variable {key!r}") from None
