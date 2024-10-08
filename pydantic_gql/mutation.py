from __future__ import annotations

from typing import Any, Iterable, Mapping, Self

from pydantic import BaseModel

from .gql_field import GqlField
from .operation import Operation
from .values import GqlValue
from .var import Var


class Mutation(Operation):
    """A GraphQL mutation object, which represents a collection of fields to modify data in a GraphQL API.

    # Usage

    To create a simple mutation with one top-level field such as `add_book`, first create a Pydantic model for the `Book` type, then create a `Mutation` object with the `Mutation.from_model` constructor.
    ```python
    class Book(BaseModel):
        title: str
        author: str

    book = Book(title="The Lord of the Rings", author="J.R.R. Tolkien")

    mutation = Mutation.from_model(Book, "add_book", args=dict(book))
    print(mutation)
    ```
    This will output:
    ```
    mutation AddBook {
      add_book(title: "The Lord of the Rings", author: "J.R.R. Tolkien") {
        title,
        author,
      },
    }
    ```

    To create a mutation with multiple top-level fields such as `add_book` and `remove_book`, use the `Mutation` constructor directly.
    ```python
    mutation = Mutation(
        "ModifyBooks",
        GqlField.from_model(Book, "add_book", args=dict(book)),
        GqlField("remove_book", args={"id": 1}),
    )
    print(mutation)
    ```
    This will output:
    ```
    mutation ModifyBooks {
      add_book(title: "The Lord of the Rings", author: "J.R.R. Tolkien") {
        title,
        author,
      },
      remove_book(id: 1),
    }
    ```

    # Formatting

    To generate the mutation string to send to the API, use `str(mutation)`. This will format the mutation with default indentation of 2 spaces.

    To customize the indentation, use `format` function or f-strings with the desired indentation level or a custom indentation string. The following are all valid:
    ```python
    f"default indentation of 2 spaces: {mutation}"
    f"same as above:                   {mutation:indent}"
    f"no indentation; all on one line: {mutation:noindent}"
    f"indentation of 4 spaces:         {mutation:4}"
    f"indentation with tabs:           {mutation:\t}"
    ```

    Args:
        name: The name of the mutation. This has no meaning in the GraphQL mutation itself; it is just a label for you to identify the mutation.
        fields: The fields to include in the mutation. These can be created manually or using the `GqlField.from_model` constructor.
        variables: The variables to include in the mutation.
    """

    def __init__(
        self, name: str, *fields: GqlField, variables: Iterable[Var[Any]] = ()
    ) -> None:
        super().__init__("mutation", name, *fields, variables=variables)

    @classmethod
    def from_model(
        cls,
        model: type[BaseModel],
        field_name: str | None = None,
        mutation_name: str | None = None,
        variables: Iterable[Var[Any]] = (),
        args: Mapping[str, GqlValue] = {},
    ) -> Self:
        """Create a mutation with a single top-level field whose subfields are defined by a Pydantic model.

        # Usage

        To create a mutation with a one top-level field such as `add_book`, first create a Pydantic model for the `Book` type, then use the `Mutation.from_model` constructor.

        ```python
        class Book(BaseModel):
            title: str
            author: str

        book = Book(title="The Lord of the Rings", author="J.R.R. Tolkien")

        mutation = Mutation.from_model(Book, "add_book", args=dict(book))
        print(mutation)
        ```
        This will output:
        ```
        mutation Book {
          add_book(title: "The Lord of the Rings", author: "J.R.R. Tolkien") {
            title,
            author,
          },
        }
        ```

        To include variables and arguments in the query, first create a subclass of `BaseVars` with the variables you want to define, then pass the variables and arguments to the constructor.

        ```python
        class RemovedBook(BaseModel):
            id: int
            archived: bool

        class Vars(BaseVars):
            id: Var[int | None] = Var(default=None)
            title: Var[str | None] = Var(default=None)

        variables = Vars(title="The Lord of the Rings")
        mutation = Mutation.from_model(
            RemovedBook,
            "remove_book",
            variables=variables,
            args={"id": Vars.id, "title": Vars.title, "archive": True},
        )
        print(mutation)
        ```
        This will output:
        ```
        mutation RemovedBook($id: Int, $title: String) {
          remove_book(id: $id, title: $title, archive: true) {
            id,
            archived,
          },
        }
        ```

        Args:
            model: The Pydantic model to use for the fields.
            field_name: The name of the top-level field. If not provided, the name of the model is used.
            mutation_name: The name of the mutation. If not provided, the name of the model is used.
            variables: The variables to include in the mutation.
            args: The arguments to pass to the top-level field.
        """

        return cls(
            mutation_name or model.__name__,
            GqlField.from_model(model, field_name, args),
            variables=variables,
        )
