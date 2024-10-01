import pytest

from pydantic_gql import Expr, Var
from pydantic_gql.builders import ValueBuilder


@pytest.fixture
def builder() -> ValueBuilder:
    return ValueBuilder()


def test_var(builder: ValueBuilder) -> None:
    assert builder.build(Var("foo")) == "$foo"


def test_expression(builder: ValueBuilder) -> None:
    assert builder.build(Expr("...")) == "..."


@pytest.mark.parametrize(
    "string, expected",
    [
        ("foo", '"foo"'),
        ('"foo"', '"\\"foo\\""'),
        ("foo\nbar", '"foo\\nbar"'),
    ],
)
def test_string(builder: ValueBuilder, string: str, expected: str) -> None:
    assert builder.build(string) == expected


def test_bool(builder: ValueBuilder) -> None:
    assert builder.build(True) == "true"
    assert builder.build(False) == "false"


def test_iterable(builder: ValueBuilder) -> None:
    assert builder.build([1, 2, 3]) == "[1, 2, 3]"
    assert builder.build(("foo", "bar")) == '["foo", "bar"]'
    assert builder.build((x for x in range(3))) == "[0, 1, 2]"


def test_int(builder: ValueBuilder) -> None:
    assert builder.build(42) == "42"


def test_float(builder: ValueBuilder) -> None:
    assert builder.build(42.42) == "42.42"


def test_none(builder: ValueBuilder) -> None:
    assert builder.build(None) == "null"
