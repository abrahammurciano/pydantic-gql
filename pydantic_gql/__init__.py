"""
.. include:: ../README.md
"""

import importlib.metadata as metadata

__version__ = metadata.version(__package__ or __name__)

from .base_vars import BaseVars
from .builders.query_builder import QueryBuilder
from .gql_field import GqlField
from .query import Query
from .values import Expr, GqlValue
from .var import Var

__all__ = ("Query", "BaseVars", "Var", "GqlField", "QueryBuilder", "Expr", "GqlValue")
