"""
.. include:: ../README.md
"""

import importlib.metadata as metadata

__version__ = metadata.version(__package__ or __name__)

from .base_vars import BaseVars
from .gql_field import GqlField
from .query import Query
from .query_formatter import QueryFormatter
from .var import Var

__all__ = ("Query", "BaseVars", "Var", "GqlField", "QueryFormatter")
