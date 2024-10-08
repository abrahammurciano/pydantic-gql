from pydantic import BaseModel

from pydantic_gql import BaseVars, Expr, GqlField, Mutation, Query, Var

from .check_op import check_op


class Book(BaseModel):
    title: str
    author: str


class Author(BaseModel):
    name: str


def test_query_from_model() -> None:
    query = Query.from_model(Book, "books")
    check_op(query, "query Book { books { title, author, }, }")


def test_query_constructor() -> None:
    query = Query(
        "BooksAndAuthors",
        GqlField.from_model(Book, "books"),
        GqlField.from_model(Author, "authors"),
    )
    check_op(
        query,
        "query BooksAndAuthors { books { title, author, }, authors { name, }, }",
    )


def test_query_with_args() -> None:
    query = Query.from_model(
        Book,
        "books",
        args={"year": 1998, "author": "Rowling", "series": Expr('"Harry Potter"')},
    )
    check_op(
        query,
        'query Book { books(year: 1998, author: "Rowling", series: "Harry Potter") { title, author, }, }',
    )


def test_query_with_vars() -> None:
    class Vars(BaseVars):
        id: Var[int]

    query = Query.from_model(Book, "books", variables=Vars, args={"bookId": Vars.id})
    check_op(query, "query Book($id: Int!) { books(bookId: $id) { title, author, }, }")


def test_mutation_from_model() -> None:
    book = Book(title="The Lord of the Rings", author="J.R.R. Tolkien")
    mutation = Mutation.from_model(Book, "add_book", args=dict(book))
    check_op(
        mutation,
        'mutation Book { add_book(title: "The Lord of the Rings", author: "J.R.R. Tolkien") { title, author, }, }',
    )


def test_mutation_constructor() -> None:
    book = Book(title="The Lord of the Rings", author="J.R.R. Tolkien")
    mutation = Mutation("AddBook", GqlField.from_model(Book, "book", args=dict(book)))
    check_op(
        mutation,
        'mutation AddBook { book(title: "The Lord of the Rings", author: "J.R.R. Tolkien") { title, author, }, }',
    )


def test_mutation_with_args() -> None:
    mutation = Mutation.from_model(
        Book,
        "add_book",
        args={
            "year": 1954,
            "author": "Tolkien",
            "series": Expr('"The Lord of the Rings"'),
        },
    )
    check_op(
        mutation,
        'mutation Book { add_book(year: 1954, author: "Tolkien", series: "The Lord of the Rings") { title, author, }, }',
    )


def test_mutation_with_vars() -> None:
    class Vars(BaseVars):
        id: Var[int | None] = Var(default=None)
        title: Var[str | None] = Var(default=None)

    class RemovedBook(BaseModel):
        id: int
        title: str
        author: str
        archived: bool

    mutation = Mutation.from_model(
        RemovedBook,
        "remove_book",
        variables=Vars,
        args={"bookId": Vars.id, "bookTitle": Vars.title},
    )

    check_op(
        mutation,
        "mutation RemovedBook($id: Int, $title: String) { remove_book(bookId: $id, bookTitle: $title) { id, title, author, archived, }, }",
    )
