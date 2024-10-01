from typing import Generic, TypeVar

from pydantic import BaseModel, Field

__all__ = ["PageInfo", "Edge", "Connection"]

_T = TypeVar("_T", bound=BaseModel)


class PageInfo(BaseModel):
    """Information about a single page of a paginated connection."""

    has_next_page: bool = Field(alias="hasNextPage")
    """Whether there is a next page."""

    has_previous_page: bool = Field(alias="hasPreviousPage")
    """Whether there is a previous page."""

    start_cursor: str = Field(alias="startCursor")
    """The cursor of the first item in the page."""

    end_cursor: str = Field(alias="endCursor")
    """The cursor of the last item in the page."""


class Edge(BaseModel, Generic[_T]):
    """An edge type for pagination.

    An edge type is used to represent a single item within a paginated connection, and contains the node itself as well as the cursor for that node.
    """

    node: _T
    """The object itself."""

    cursor: str
    """A cursor pointing to the object within the paginated connection."""


class Connection(BaseModel, Generic[_T]):
    """A connection type for pagination.

    This class is used to represent a connection type for pagination in a GraphQL API.
    """

    edges: list[Edge[_T]]
    """A list of edges in the connection."""

    page_info: PageInfo = Field(alias="pageInfo")
