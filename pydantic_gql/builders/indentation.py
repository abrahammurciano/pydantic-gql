from typing import Self


class Indentation:
    def __init__(self, indentation: str | None = "  ", level: int = 0) -> None:
        self._indentation = indentation
        self._level = level

    def __str__(self) -> str:
        return (
            "\n" + self._indentation * self._level
            if self._indentation is not None
            else ""
        )

    def __add__(self, other: int) -> Self:
        return type(self)(self._indentation, self._level + other)
