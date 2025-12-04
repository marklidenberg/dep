from typing import Callable, Dict
from dep import _overrides, _cache

def override(mapping: Dict[Callable, Callable]) -> None:
    """
    Override dependency functions with new implementations.

    Args:
        mapping: Dictionary mapping original functions to their overrides
    """

    # - Update override mappings

    _overrides.update(mapping)

    # - Clear cache when overrides are set

    _cache.clear()
