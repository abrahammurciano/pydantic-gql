from __future__ import annotations

from typing import (
    Any,
    ClassVar,
    Iterable,
    Iterator,
    Mapping,
    dataclass_transform,
    get_origin,
    get_type_hints,
)

from pydantic_gql.var import Var


def _is_var(annotation: Any) -> bool:
    """Check if a type annotation (from typing.get_type_hints) is a `Var`."""
    origin = get_origin(annotation)
    return origin is not ClassVar and issubclass(origin or annotation, Var)


@dataclass_transform(eq_default=False, field_specifiers=(Var,))
class BaseVarsMeta(type, Iterable[Var[Any]]):
    def __iter__(self: type[BaseVars]) -> Iterator[Var[Any]]:
        return iter(self.__variables__.values())


class BaseVars(Mapping[Var[Any], Any], metaclass=BaseVarsMeta):
    __variables__: ClassVar[Mapping[str, Var[Any]]]

    def __init_subclass__(cls) -> None:
        cls.__variables__ = {}
        for name, annotation in get_type_hints(cls).items():
            if not _is_var(annotation):
                continue
            value = getattr(cls, name, None)
            if isinstance(value, Var):
                name = value.name or name
                cls.__variables__[name] = Var(
                    name, value.default, value.var_type or annotation.__args__[0]
                )
            else:
                cls.__variables__[name] = Var(name, value, annotation.__args__[0])
        for name, var in cls.__variables__.items():
            setattr(cls, name, var)

    def __init__(self, **kwargs: Any) -> None:
        self.__values__ = {
            name: kwargs.get(name, var.default)
            for name, var in self.__variables__.items()
        }

    def __iter__(self) -> Iterator[Var[Any]]:
        return iter(self.__variables__.values())


# Example usage
class Vars(BaseVars):
    var1: Var[str]
    var2: Var[int] = Var(default=42)
    var3: Var[int] = Var(default=69, type=int, name="thirdVar")


my_vars = Vars(var1="value-1")

assert my_vars.var1 == "value-1", my_vars.var1
assert isinstance(Vars.var1, Var), Vars.var1
assert my_vars.var2 == 42, my_vars.var2
assert isinstance(Vars.__variables__, dict), Vars.__variables__
assert isinstance(my_vars.__variables__, dict), my_vars.__variables__

other_vars = Vars(var1="value-2")
other_vars.var2 = 100
other_vars.var3 = 200
assert my_vars.var2 == 42, my_vars.var2
assert my_vars.var3 == 69, my_vars.var3
