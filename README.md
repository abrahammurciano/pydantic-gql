# pydantic-gql
A simple GraphQL query builder based on Pydantic models

## Installation

You can install this package with pip.
```sh
$ pip install pydantic-gql
```

## Links

[![Documentation](https://img.shields.io/badge/Documentation-C61C3E?style=for-the-badge&logo=Read+the+Docs&logoColor=%23FFFFFF)](https://abrahammurciano.github.io/pydantic-gql)

[![Source Code - GitHub](https://img.shields.io/badge/Source_Code-GitHub-181717?style=for-the-badge&logo=GitHub&logoColor=%23FFFFFF)](https://github.com/abrahammurciano/pydantic-gql.git)

[![PyPI - pydantic-gql](https://img.shields.io/badge/PyPI-pydantic_gql-006DAD?style=for-the-badge&logo=PyPI&logoColor=%23FFD242)](https://pypi.org/project/pydantic-gql/)

## Usage

To use `pydantic-gql`, you need to define your Pydantic models and then use them to build GraphQL queries. The core classes you'll interact with is the `Query` class to create queries and the `Mutation` class to create mutations. (Both queries and mutations are types of "operations".)

### Queries

#### Defining Pydantic Models

First, define your Pydantic models that represent the structure of the data you want to query. Here's an example:

```python
from pydantic import BaseModel

class Group(BaseModel):
    id: int
    name: str

class User(BaseModel):
    id: int
    name: str
    groups: list[Group]
```

#### Building a Query

Most GraphQL queries contain a single top-level field. Since this is the most common use case, this library provides `Query.from_model()` as a convenience method to create a query with one top-level field whose subfields are defined by the Pydantic model.

```python
from pydantic_gql import Query

query = Query.from_model(User)
```

This will create a query that looks like this:

```graphql
query User{
  User {
    id,
    name,
    groups {
      id,
      name,
    },
  },
}
```

This method also provides parameters to customise the query, such as the query name, field name, variables (see [Using Variables](#using-variables) for examples with variables), and arguments. Here's a more complex example:

```python
query = Query.from_model(
    User,
    query_name="GetUser",
    field_name="users",
    arguments={"id": 1},
)
```

This will create a query that looks like this:

```graphql
query GetUser{
  users(id: 1) {
    id,
    name,
    groups {
      id,
      name,
    },
  },
}
```

### Mutations

Since both queries and mutations are types of operations, the `Mutation` class works in the same way as the `Query` class. Here's an example of how to build a mutation that could create a new user and return their data.

```python
from pydantic_gql import Mutation

new_user = User(id=1, name="John Doe", groups=[])
mutation = Mutation.from_model(User, "create_user", args=dict(new_user))
```

This will create a mutation that looks like this:

```graphql
mutation CreateUser {
  createUser(id: 1, name: "John Doe", groups: []) {
	id,
	name,
	groups {
	  id,
	  name,
	},
  },
}
```

### Generating the GraphQL Operation String

To get the actual GraphQL query or mutation as a string that you can send to your server, simply convert the `Query` or `Mutation` object to a string.

```python
query_string = str(query)
```

You can control the indentation of the resulting string by using `format()` instead of `str()`. Valid values for the format specifier are:

- `indent` - The default. Indent the resulting string with two spaces.
- `noindent` - Do not indent the resulting string. The result will be a single line.
- A number - Indent the resulting string with the specified number of spaces.
- A whitespace string - Indent the resulting string with the specified string, e.g. `\t`.

```python
query_string = format(query, '\t')
```

### Using Variables

A GraphQL query can define variables at the top and then reference them throughout the rest of the operation. Then when the operation is sent to the server, the variables are passed in a separate dictionary.

To define variables for a GraphQL operation, first create a class that inherits from `BaseVars` and define the variables as attributes with `Var[T]` as the type annotation.

```python
from pydantic_gql import BaseVars, Var

class UserVars(BaseVars):
    age: Var[int]
    group: Var[str | None]
    is_admin: Var[bool] = Var(default=False)
```

You can pass the class itself to the `.from_model()` method to include the variables in the query. You can also reference the class attributes in the operation's arguments directly.

```python
query = Query.from_model(
    User,
    variables=UserVars,
    args={"age": UserVars.age, "group": UserVars.group, "isAdmin": UserVars.is_admin},
)
```

This will create a query that looks like this:

```graphql
query User($age: Int!, $group: String, $is_admin: Boolean = false){
  User(age: $age, group: $group, isAdmin: $is_admin) {
    id,
    name,
    groups {
      id,
      name,
    },
  },
}
```

When you want to send the query, you can instantiate the variables class, which itself is a `Mapping` of variable names to values, and pass it to your preferred HTTP client.

```python
variables = UserVars(age=18, group="admin", is_admin=True)
httpx.post(..., json={"query": str(query), "variables": dict(variables)})
```

### More Complex Operations

Sometimes you may need to build more complex operations than the ones we've seen so far. For example, you may need to include multiple top-level fields, or you may need to provide arguments to some deeply nested fields.

> In the following examples we'll be using queries, but the same principles apply to mutations.

In these cases, you can build the query manually with the `Query` constructor. The constructor takes the query name followed by any number of `GqlField` objects, then optionally `variables` as a keyword argument.

`GqlField`s themselves can also be constructed with their `from_model()` convenience method or manually with their constructor.

Here's an example of a more complex query:

```python
from pydantic import BaseModel, Field
from pydantic_gql import Query, GqlField, BaseVars

class Vars(BaseVars):
    min_size: Var[int] = Var(default=0)
    groups_per_user: Var[int | None]

class PageInfo(BaseModel):
    has_next_page: bool = Field(alias="hasNextPage")
    end_cursor: str | None = Field(alias="endCursor")

class GroupEdge(BaseModel):
    node: Group
    cursor: str

class GroupConnection(BaseModel):
    edges: list[GroupEdge]
    page_info: PageInfo = Field(alias="pageInfo")

query = Query(
    "GetUsersAndGroups",
    GqlField(
        name="users",
        args={"minAge": 18},
        fields=(
            GqlField("id"),
            GqlField("name"),
            GqlField.from_model(GroupConnection, "groups", args={"first": Vars.groups_per_user}),
        ),
    )
    GqlField.from_model(Group, "groups", args={"minSize": Vars.min_size}),
    variables=Vars,
)
```

This will create a query that looks like this:

```graphql
query GetUsersAndGroups($min_size: Int = 0, $groups_per_user: Int){
  users(minAge: 18) {
    id,
    name,
    groups(first: $groups_per_user) {
      edges {
        node {
          id,
          name,
        },
        cursor,
      },
      pageInfo {
        hasNextPage,
        endCursor,
      },
    },
  },
  groups(minSize: $min_size) {
    id,
    name,
  },
}
```

### Connections (Pagination)

The previous example demonstrates how to build a query that uses pagination. However, since pagination is a common pattern (see the [GraphQL Connections Specification](https://relay.dev/graphql/connections.htm)), this library provides a `Connection` class which is generic over the node type. You can use this class to easily build pagination queries.

Here's an example of how to use the `Connection` class:

```python
from pydantic_gql.connections import Connection

query = Query.from_model(
    Connection[User],
    "users",
    args={"first": 10},
)
```

This will create a query that looks like this:

```graphql
query User{
  users(first: 10) {
    edges {
      node {
        id,
        name,
        groups {
          id,
          name,
        },
      },
      cursor,
    },
    pageInfo {
      hasNextPage,
      endCursor,
    },
  },
}
```
