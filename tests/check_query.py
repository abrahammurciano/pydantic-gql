import re

from pydantic_gql.query import Query


def check_query(query: Query, expected: str) -> None:
    assert _normalize(str(query)) == _normalize(expected)


def _normalize(query: str) -> str:
    result = re.sub(r"\s+", " ", query)
    result = re.sub(r"\s*{\s*", "{", result)
    result = re.sub(r"\s*}\s*", "}", result)
    result = re.sub(r"\s*,\s*", ",", result)
    return result.strip()
