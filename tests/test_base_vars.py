import pytest

from pydantic_gql import BaseVars, Var


class Vars(BaseVars):
    a: Var[int]
    b: Var[str | None]
    c: Var[bool] = Var(default=True)
    d: Var[int] = Var(name="D")


def test_vars() -> None:
    assert Vars.a.name == "a"
    assert Vars.a.var_type == int
    assert Vars.a.required
    with pytest.raises(ValueError):
        Vars.a.default

    assert Vars.b.name == "b"
    assert Vars.b.var_type == str | None
    assert not Vars.b.required
    assert Vars.b.default is None

    assert Vars.c.name == "c"
    assert Vars.c.var_type == bool
    assert not Vars.c.required
    assert Vars.c.default is True

    assert Vars.d.name == "D"
    assert Vars.d.var_type == int
    assert Vars.d.required
    with pytest.raises(ValueError):
        Vars.d.default


def test_dunder_variables() -> None:
    assert Vars.__variables__ == {
        "a": Vars.a,
        "b": Vars.b,
        "c": Vars.c,
        "d": Vars.d,
    }


def test_iter_vars() -> None:
    assert list(Vars) == [Vars.a, Vars.b, Vars.c, Vars.d]


def test_vars_init() -> None:
    variables = Vars(a=1, b="2", c=False, d=3)
    assert variables.a == 1
    assert variables.b == "2"
    assert variables.c is False
    assert variables.d == 3

    with pytest.raises(TypeError):
        Vars(1, 2, 3, 4)  # type: ignore


def test_vars_init_defaults() -> None:
    variables = Vars(a=1, b="2", d=3)
    assert variables.a == 1
    assert variables.b == "2"
    assert variables.c is True
    assert variables.d == 3


def test_vars_init_missing_required() -> None:
    with pytest.raises(TypeError):
        Vars(a=1, b="2")  # type: ignore


def test_dunder_values() -> None:
    variables = Vars(a=1, b="2", c=False, d=3)
    assert variables.__values__ == {
        "a": 1,
        "b": "2",
        "c": False,
        "D": 3,
    }
