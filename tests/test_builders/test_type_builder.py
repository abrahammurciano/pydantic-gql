from datetime import datetime
from typing import Any, Iterable, Mapping, Optional, Union

import pytest

from pydantic_gql import Var
from pydantic_gql.builders import TypeBuilder


@pytest.fixture
def builder() -> TypeBuilder:
    return TypeBuilder()


def test_basic_types(builder: TypeBuilder) -> None:
    assert builder.build(Var(type=str)) == "String!"
    assert builder.build(Var[int]()) == "Int!"


@pytest.mark.parametrize(
    "var", (Var[Union[str, None]](), Var[Optional[str]](), Var[str | None]())
)
def test_optional_type(builder: TypeBuilder, var: Var[Any]) -> None:
    assert builder.build(var) == "String"


@pytest.mark.parametrize(
    "var",
    (
        Var[Union[str, int]](),
        Var[str | int](),
        Var[Union[str, int, None]](),
        Var[str | int | None](),
    ),
)
def test_invalid_union_type(builder: TypeBuilder, var: Var[Any]) -> None:
    with pytest.raises(ValueError):
        builder.build(var)


@pytest.mark.parametrize(
    "var, expected",
    (
        (Var[Iterable[str]](), "[String!]!"),
        (Var[Iterable[str]](default=[]), "[String!]"),
        (Var[Iterable[str | None]](), "[String]!"),
        (Var[list[str]](), "[String!]!"),
        (Var[list[list[str]]](), "[[String!]!]!"),
        (Var[list[list[str] | None]](), "[[String!]]!"),
    ),
)
def test_iterable_type(builder: TypeBuilder, var: Var[Any], expected: str) -> None:
    assert builder.build(var) == expected


def test_invalid_iterable_type(builder: TypeBuilder) -> None:
    var = Var[Mapping[str, int]]()
    with pytest.raises(ValueError):
        builder.build(var)


def test_custom_type(builder: TypeBuilder) -> None:
    class CustomType: ...
    var = Var[CustomType]()
    assert builder.build(var) == f"{CustomType.__name__}!"


@pytest.mark.parametrize(
    "var, expected",
    (
        (Var[datetime](type_name="Date"), "Date!"),
        (Var[Union[str, int]](type_name="Date"), "Date!"),
        (Var[Iterable[str]](type_name="Date"), "[Date!]!"),
    ),
)
def test_custom_type_name(builder: TypeBuilder, var: Var[Any], expected: str) -> None:
    assert builder.build(var) == expected


def test_unknown_type(builder: TypeBuilder) -> None:
    with pytest.raises(ValueError):
        builder.build(Var())
