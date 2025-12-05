from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar, Generator, AsyncGenerator, overload
from contextlib import contextmanager, asynccontextmanager
import asyncio
import inspect

T = TypeVar("T")

# - Module-level state

_cache: dict[tuple, Any] = {}
_overrides: dict[Callable, Callable] = {}


def _normalize_value(value: Any) -> Any:
    """Convert dicts to sorted tuples for proper caching."""
    if isinstance(value, dict):
        return tuple(sorted(value.items()))
    return value


@overload
def dep(
    cached: bool = False,
) -> Callable[[Callable[..., Generator[T, None, None]]], Callable[..., "contextmanager[T]"]]: ...


@overload
def dep(
    cached: bool = False,
) -> Callable[
    [Callable[..., AsyncGenerator[T, None]]], Callable[..., "asynccontextmanager[T]"]
]: ...


def dep(cached: bool = False):
    """
    Decorator for dependency injection with optional caching.

    Args:
        cached: If True, the result will be cached and reused for the duration of the context
    """

    def decorator(func: Callable[..., Generator[T, None, None]]) -> Callable[..., contextmanager[T]]:
        @wraps(func)
        @contextmanager
        def sync_wrapper(*args, **kwargs) -> Generator[T, None, None]:
            # - Resolve target function

            target_func = _overrides.get(func, default=func)

            # - Build cache key

            normalized_args = tuple(_normalize_value(arg) for arg in args)
            normalized_kwargs = tuple(sorted((k, _normalize_value(v)) for k, v in kwargs.items()))
            cache_key = (target_func, normalized_args, normalized_kwargs)

            # - Check cache if enabled

            if cached and cache_key in _cache:
                yield _cache[cache_key]
                return

            # - Execute function and get result

            result_gen = target_func(*args, **kwargs)

            # - Extract yielded value

            try:
                result = next(result_gen)
            except StopIteration:
                raise RuntimeError(f"{func.__name__} did not yield a value")

            if cached:
                _cache[cache_key] = result

            try:
                yield result
            finally:
                # - Cleanup: run generator to completion

                try:
                    next(result_gen)
                except StopIteration:
                    pass

                # - Remove from cache after cleanup

                if cached and cache_key in _cache:
                    del _cache[cache_key]

        @wraps(func)
        @asynccontextmanager
        async def async_wrapper(*args, **kwargs) -> AsyncGenerator[T, None]:
            # - Resolve target function

            target_func = _overrides.get(func, func)

            # - Build cache key

            normalized_args = tuple(_normalize_value(arg) for arg in args)
            normalized_kwargs = tuple(sorted((k, _normalize_value(v)) for k, v in kwargs.items()))
            cache_key = (target_func, normalized_args, normalized_kwargs)

            # - Check cache if enabled

            if cached and cache_key in _cache:
                yield _cache[cache_key]
                return

            # - Execute function and get result

            result_gen = target_func(*args, **kwargs)

            # - Extract yielded value

            try:
                result = await result_gen.__anext__()
            except StopAsyncIteration:
                raise RuntimeError(f"{func.__name__} did not yield a value")

            if cached:
                _cache[cache_key] = result

            try:
                yield result
            finally:
                # - Cleanup: run generator to completion

                try:
                    await result_gen.__anext__()
                except StopAsyncIteration:
                    pass

                # - Remove from cache after cleanup

                if cached and cache_key in _cache:
                    del _cache[cache_key]

        # - Determine wrapper type based on function type

        if asyncio.iscoroutinefunction(func) or inspect.isasyncgenfunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def test():
    # - Test sync dependency with caching

    @dep()
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
