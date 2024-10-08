import re

from pydantic_gql.operation import Operation


def check_op(op: Operation, expected: str) -> None:
    assert _normalize(str(op)) == _normalize(expected)


def _normalize(op: str) -> str:
    result = re.sub(r"\s+", " ", op)
    result = re.sub(r"\s*{\s*", "{", result)
    result = re.sub(r"\s*}\s*", "}", result)
    result = re.sub(r"\s*,\s*", ",", result)
    return result.strip()
