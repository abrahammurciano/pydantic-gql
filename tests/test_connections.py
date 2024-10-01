import pytest
from pydantic import BaseModel

from pydantic_gql import Query
from pydantic_gql.connections import Connection

from .check_query import check_query


class Item(BaseModel):
    id: int
    name: str


@pytest.fixture
def query() -> Query:
    return Query.from_model(
        Connection[Item], "items", "ConnectionTest", args={"first": 10}
    )


def test_connection(query: Query) -> None:
    check_query(
        query,
        """
        query ConnectionTest {
            items(first: 10) {
                edges {
                    node {
                        id,
                        name,
                    },
                    cursor,
                },
                pageInfo {
                    hasNextPage,
                    hasPreviousPage,
                    startCursor,
                    endCursor,
                },
            },
        }
        """,
    )
