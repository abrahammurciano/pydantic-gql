import pytest

from pydantic_gql.builders import ArgsBuilder


@pytest.fixture
def builder() -> ArgsBuilder:
    return ArgsBuilder()


def test_empty_args(builder: ArgsBuilder) -> None:
    assert builder.build({}) == "()"


def test_single_arg(builder: ArgsBuilder) -> None:
    assert builder.build({"arg": "value"}) == '(arg: "value")'


def test_multiple_args(builder: ArgsBuilder) -> None:
    assert builder.build({"a": "1", "b": "2"}) == '(a: "1", b: "2")'
