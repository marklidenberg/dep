from functools import wraps
from typing import Any, Callable, TypeVar
import asyncio
import inspect

from dep.sync_context_manager import SyncContextManager
from dep.async_context_manager import AsyncContextManager

T = TypeVar('T')

# - Module-level state

_cache: dict[Callable, Any] = {}
_overrides: dict[Callable, Callable] = {}


def dep(cached: bool = True):
    """
    Decorator for dependency injection with optional caching.

    Args:
        cached: If True, the result will be cached and reused
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:

        @wraps(func)
        def sync_wrapper(*args, **kwargs):

            # - Resolve target function

            target_func = _overrides.get(func, func)

            # - Build cache key

            cache_key = (target_func, args, tuple(sorted(kwargs.items())))

            # - Check cache if enabled

            if cached and cache_key in _cache:
                return SyncContextManager(_cache[cache_key])

            # - Execute function and get result

            result_gen = target_func(*args, **kwargs)

            # - Extract yielded value

            try:
                result = next(result_gen)

                if cached:
                    _cache[cache_key] = result

                return SyncContextManager(result, result_gen)

            except StopIteration:
                raise RuntimeError(f"{func.__name__} did not yield a value")

        @wraps(func)
        async def async_wrapper(*args, **kwargs):

            # - Resolve target function

            target_func = _overrides.get(func, func)

            # - Build cache key

            cache_key = (target_func, args, tuple(sorted(kwargs.items())))

            # - Check cache if enabled

            if cached and cache_key in _cache:
                return AsyncContextManager(_cache[cache_key])

            # - Execute function and get result

            result_gen = target_func(*args, **kwargs)

            # - Extract yielded value

            try:
                result = await result_gen.__anext__()

                if cached:
                    _cache[cache_key] = result

                return AsyncContextManager(result, result_gen)

            except StopAsyncIteration:
                raise RuntimeError(f"{func.__name__} did not yield a value")

        # - Determine wrapper type based on function type

        if asyncio.iscoroutinefunction(func) or inspect.isasyncgenfunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def test():

    # - Test sync dependency with caching

    @dep(cached=True)
    def get_value(x: str):
        yield x

    with get_value("test") as value:
        assert value == "test"

    # - Test sync dependency without caching

    @dep(cached=False)
    def get_value_no_cache(x: str):
        yield x * 2

    with get_value_no_cache("test") as value:
        assert value == "testtest"

    # - Test async dependency with caching

    async def test_async():
        @dep(cached=True)
        async def get_async_value(x: str):
            yield x

        async with get_async_value("async_test") as value:
            assert value == "async_test"

    import asyncio
    asyncio.run(test_async())


if __name__ == "__main__":
    test()