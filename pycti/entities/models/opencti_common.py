"""OpenCTI common models"""

from typing import Literal

__all__ = [
    "FilterMode",
    "OrderingMode",
]

FilterMode = Literal["and", "or"]
OrderingMode = Literal["asc", "desc"]
