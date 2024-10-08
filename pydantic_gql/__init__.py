"""
.. include:: ../README.md
"""

import importlib.metadata as metadata

__version__ = metadata.version(__package__ or __name__)

from .base_vars import BaseVars
from .gql_field import GqlField
from .mutation import Mutation
from .query import Query
from .values import Expr, GqlValue
from .var import Var

__all__ = ("Query", "Mutation", "BaseVars", "Var", "GqlField", "Expr", "GqlValue")
