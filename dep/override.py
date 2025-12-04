from __future__ import annotations

from typing import Callable
from dep._dep import _overrides, _cache


def override(mapping: dict[Callable, Callable]) -> None:
    """
    Override dependency functions with new implementations.

    Args:
        mapping: Dictionary mapping original functions to their override functions
    """

    # - Update override mappings

    _overrides.update(mapping)

    # - Clear cache when overrides are set

    _cache.clear()


def test():
    # - Test override functionality

    from dep._dep import dep

    @dep()
    def get_foo(bar: str):
        yield bar

    @dep()
    def new_get_foo(bar: str):
        yield bar * 2

    # - Test original function

    with get_foo(bar="bar") as foo:
        assert foo == "bar"

    # - Apply override

    override({get_foo: new_get_foo})

    # - Test overridden function

    with get_foo(bar="bar") as foo:
        assert foo == "barbar"
