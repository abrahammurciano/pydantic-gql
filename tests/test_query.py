from pydantic import BaseModel

from pydantic_gql import BaseVars, Expr, GqlField, Query, Var

from .check_query import check_query


class Book(BaseModel):
    title: str
    author: str


class Author(BaseModel):
    name: str


def test_query_from_model() -> None:
    query = Query.from_model(Book, "books")
    check_query(query, "query Book { books { title, author, }, }")


def test_query_constructor() -> None:
    query = Query(
        "BooksAndAuthors",
        GqlField.from_model(Book, "books"),
        GqlField.from_model(Author, "authors"),
    )
    check_query(
        query,
        "query BooksAndAuthors { books { title, author, }, authors { name, }, }",
    )


def test_query_with_args() -> None:
    query = Query.from_model(
        Book,
        "books",
        args={"year": 1998, "author": "Rowling", "series": Expr('"Harry Potter"')},
    )
    check_query(
        query,
        'query Book { books(year: 1998, author: "Rowling", series: "Harry Potter") { title, author, }, }',
    )


def test_query_with_vars() -> None:
    class Vars(BaseVars):
        id: Var[int]

    query = Query.from_model(Book, "books", variables=Vars, args={"bookId": Vars.id})
    check_query(
        query, "query Book($id: Int!) { books(bookId: $id) { title, author, }, }"
    )
