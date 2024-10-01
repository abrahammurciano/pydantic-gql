from abc import ABC, abstractmethod
from io import StringIO
from typing import Generic, TypeVar, overload

T = TypeVar("T")


class Builder(ABC, Generic[T]):
    """Base class for all GraphQL builders.

    A builder is a class that converts an object that represents some GraphQL construct into actual GraphQL code.

    Classes that inherit from this class must implement the `insert` method which takes the source object (of type `T`) and a `StringIO` buffer and inserts the GraphQL code into the buffer.
    """

    def build(self, source: T, /) -> str:
        """Convert a source object into a GraphQL string.

        Args:
            source: The source object to convert.

        Returns:
            The source object as a string of GraphQL code.
        """
        result = StringIO()
        self.insert(source, result)
        return result.getvalue()

    @abstractmethod
    def insert(self, source: T, buffer: StringIO, /) -> None:
        """Insert the GraphQL code for the source object into the result buffer.

        Args:
            source: The source object to convert.
            buffer: The buffer to insert the GraphQL code into.
        """

    @overload
    def __call__(self, source: T, /) -> str: ...

    @overload
    def __call__(self, source: T, buffer: StringIO, /) -> None: ...

    def __call__(self, source: T, buffer: StringIO | None = None) -> str | None:
        if buffer:
            return self.insert(source, buffer)
        return self.build(source)
