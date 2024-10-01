import pytest
from pydantic import BaseModel

from pydantic_gql import Query


class Book(BaseModel):
    title: str
    author: str


@pytest.fixture
def query() -> Query:
    return Query.from_model(Book, "books")


def test_default_formatting(query: Query) -> None:
    assert f"{query}" == "query Book {\n  books {\n    title,\n    author,\n  },\n}"


def test_indent_formatting(query: Query) -> None:
    assert (
        f"{query:indent}" == "query Book {\n  books {\n    title,\n    author,\n  },\n}"
    )


def test_noindent_formatting(query: Query) -> None:
    assert f"{query:noindent}" == "query Book {books {title,author,},}"


def test_1_indent_formatting(query: Query) -> None:
    assert f"{query:1}" == "query Book {\n books {\n  title,\n  author,\n },\n}"


def test_tab_indent_formatting(query: Query) -> None:
    assert f"{query:\t}" == "query Book {\n\tbooks {\n\t\ttitle,\n\t\tauthor,\n\t},\n}"
