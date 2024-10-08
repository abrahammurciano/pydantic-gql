from __future__ import annotations

from typing import Any, Iterable, Mapping, Self

from pydantic import BaseModel

from .gql_field import GqlField
from .operation import Operation
from .values import GqlValue
from .var import Var


class Query(Operation):
    """A GraphQL query object, which is a collection of fields to be queried from a GraphQL API.

    # Usage

    To create simple query with one top-level field such as `books`, first create a Pydantic model for the `Book` type, then create a `Query` object with the `Query.from_model` constructor.
    ```python
    class Book(BaseModel):
        title: str
        author: str

    query = Query.from_model(Book, "books")
    print(query)
    ```
    This will output:
    ```
    query Book {
      books {
        title
        author
      }
    }
    ```

    To create a query with multiple top-level fields such as `books` and `authors`, use the `Query` constructor directly.
    ```python
    class Author(BaseModel):
        name: str

    query = Query(
        "BooksAndAuthors",
        GqlField.from_model(Book, "books"),
        GqlField.from_model(Author, "authors"),
    )
    print(query)
    ```
    This will output:
    ```
    query BooksAndAuthors {
      books {
        title,
        author,
      },
      authors {
        name,
      },
    }
    ```

    # Formatting

    To generate the query string to send to the API, use `str(query)`. This will format the query with default indentation of 2 spaces.

    To customize the indentation, use `format` function or f-strings with the desired indentation level or a custom indentation string. The following are all valid:
    ```python
    f"default indentation of 2 spaces: {query}"
    f"same as above:                   {query:indent}"
    f"no indentation; all on one line: {query:noindent}"
    f"indentation of 4 spaces:         {query:4}"
    f"indentation with tabs:           {query:\t}"
    ```

    Args:
        name: The name of the query. This has no meaning in the GraphQL query itself; it is just a label for you to identify the query.
        fields: The fields to include in the query. These can be created manually or using the `GqlField.from_model` constructor.
        variables: The variables to include in the query.
    """

    def __init__(
        self, name: str, *fields: GqlField, variables: Iterable[Var[Any]] = ()
    ) -> None:
        super().__init__("query", name, *fields, variables=variables)

    @classmethod
    def from_model(
        cls,
        model: type[BaseModel],
        field_name: str | None = None,
        query_name: str | None = None,
        variables: Iterable[Var[Any]] = (),
        args: Mapping[str, GqlValue] = {},
    ) -> Self:
        """Create a query with a single top-level field whose subfields are defined by a Pydantic model.

        # Usage

        To create a query with a single top-level field such as `books`, first create a Pydantic model for the `Book` type, then use the `Query.from_model` constructor.

        ```python
        class Book(BaseModel):
            title: str
            author: str

        query = Query.from_model(Book, "books")
        print(query)
        ```
        This will output:
        ```
        query Book {
          books {
            title,
            author,
          },
        }
        ```

        To include variables and arguments in the query, first create a subclass of `BaseVars` with the variables you want to define, then pass the variables and arguments to the constructor.

        ```python
        class Vars(BaseVars):
            year: Var[int]
            genre: Var[str] = Var(default="fiction")

        query = Query.from_model(Book, "books", variables=Vars(year=2021), args={"genre": Vars.genre, "year": Vars.year, "limit": 10})
        print(query)
        ```
        This will output:
        ```
        query Book($year: Int!, $genre: String = "fiction") {
          books(genre: $genre, year: $year, limit: 10) {
            title,
            author,
          },
        }
        ```

        Args:
            model: The Pydantic model to use for the fields.
            field_name: The name of the top-level field. If not provided, the name of the model is used.
            query_name: The name of the query. If not provided, the name of the model is used.
            variables: The variables to include in the query.
            args: The arguments to pass to the top-level field.
        """
        return cls(
            query_name or model.__name__,
            GqlField.from_model(model, field_name, args),
            variables=variables,
        )
