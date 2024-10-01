from dataclasses import dataclass, field
from typing import Iterable, Mapping, Self, Sequence, get_args, get_origin

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from .values import GqlValue


@dataclass
class GqlField:
    """A GraphQL field.

    This class is used to represent a field in a GraphQL query. Fields can have arguments and subfields.

    Args:
        name: The name of the field.
        args: A mapping of argument names to argument values.
        fields: A sequence of subfields.
    """

    name: str
    """The name of the field."""

    args: Mapping[str, GqlValue] = field(default_factory=dict)
    """A mapping of argument names to argument values for the field."""

    fields: Sequence[Self] = ()
    """A sequence of subfields for the field."""

    @classmethod
    def from_model(
        cls,
        model: type[BaseModel],
        name: str | None = None,
        args: Mapping[str, GqlValue] = {},
    ) -> Self:
        """Create a `GqlField` from a Pydantic model.

        This method will create a `GqlField` with the same name as the model, and with fields corresponding to the model's fields.

        Args:
            model: The Pydantic model to create a field from.
            name: The name of the field. If not provided, the name of the model will be used.
            args: A mapping of argument names to argument values for the field.

        Returns:
            A `GqlField` representing the model.
        """
        return cls(name or model.__name__, fields=cls.fields_of_model(model), args=args)

    @classmethod
    def fields_of_model(cls, model: type[BaseModel]) -> Sequence[Self]:
        """Get the GraphQL fields corresponding to a Pydantic model."""
        return tuple(
            cls.from_pydantic_field(name, field)
            for name, field in model.model_fields.items()
        )

    @classmethod
    def from_pydantic_field(cls, name: str, field: FieldInfo) -> Self:
        """Create a `GqlField` from a Pydantic field."""
        submodel = _model_of(field)
        return cls(
            name=(
                field.validation_alias
                if isinstance(field.validation_alias, str)
                else name
            ),
            fields=cls.fields_of_model(submodel) if submodel else (),
        )


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
