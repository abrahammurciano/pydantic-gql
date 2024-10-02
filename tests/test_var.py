from typing import Any, Optional, cast

import pytest

from pydantic_gql import Var


def test_var_initialization():
    var = Var(name="v", default=42, type=int)
    assert var.name == "v"
    assert var.default == 42
    assert var.var_type == int


def test_default_not_required() -> None:
    assert not Var("v", default=42, type=int).required


def test_no_default_required() -> None:
    assert Var("v", type=int).required
    assert Var[int]("v").required


def test_optional_not_required() -> None:
    assert not Var[int | None]("v").required
    assert not Var("v", type=cast(type, Optional[int])).required
    assert not Var("v", type=cast(type, int | None)).required


def test_optional_default() -> None:
    assert Var[int | None]("v").default is None


def test_required_default() -> None:
    var = Var("v", type=int)
    with pytest.raises(ValueError):
        _ = var.default


def test_set_default_name() -> None:
    var = Var(type=int)
    var.set_default_name("v")
    assert var.name == "v"


def test_set_default_type() -> None:
    var = Var[Any]("v")
    var.set_default_type(int)
    assert var.var_type == int
