from dataclasses import dataclass, field
from io import StringIO
from typing import Iterable, Mapping, Self, Sequence, get_args, get_origin

from pydantic import BaseModel
from pydantic.fields import FieldInfo


@dataclass
class GqlField:
    name: str
    remote_name: str | None = None
    args: Mapping[str, object] = field(default_factory=dict)
    fields: Sequence[Self] = ()

    @classmethod
    def from_model(
        cls,
        model: type[BaseModel],
        name: str | None = None,
        args: Mapping[str, object] = {},
    ) -> Self:
        return cls(name or model.__name__, fields=cls.fields_of_model(model), args=args)

    @classmethod
    def fields_of_model(cls, model: type[BaseModel]) -> Sequence[Self]:
        return tuple(
            cls.from_pydantic_field(name, field)
            for name, field in model.model_fields.items()
        )

    @classmethod
    def from_pydantic_field(cls, name: str, field: FieldInfo) -> Self:
        submodel = _model_of(field)
        return cls(
            name=name,
            fields=cls.fields_of_model(submodel) if submodel else (),
            remote_name=(
                field.validation_alias
                if isinstance(field.validation_alias, str)
                else None
            ),
        )

    def __str__(self) -> str:
        result = StringIO()
        result.write(self.name)
        if self.remote_name:
            result.write(f": {self.remote_name}")
        if self.fields:
            result.write(f" {{{', '.join(str(f) for f in self.fields)}}}")
        return result.getvalue()


def _model_of(field: FieldInfo) -> type[BaseModel] | None:
    """Get the model class of a Pydantic field.

    This also supports fields whose type is a collection of nested models.

    For example, for a field of type `NestedModel`, `list[NestedModel]`, etc, this function will return `NestedModel`; but for a field of type `str`, `int`, Iterable[bool], etc, it will return None.
    """
    if field.annotation is None:
        return None
    if isinstance(field.annotation, type) and issubclass(field.annotation, BaseModel):
        return field.annotation
    generic_type = get_origin(field.annotation)
    generic_args = get_args(field.annotation)
    if (
        generic_type
        and issubclass(generic_type, Iterable)
        and len(generic_args) == 1
        and issubclass(generic_args[0], BaseModel)
    ):
        return generic_args[0]
    return None
