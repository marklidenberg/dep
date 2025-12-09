from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar, Generator, AsyncGenerator, Union
from contextlib import contextmanager, asynccontextmanager
from contextvars import ContextVar
import asyncio
import inspect
import json

T = TypeVar("T")

# - Module-level state

_cache: dict[str, Any] = {}
_context_stack: ContextVar[list[dict[Callable, Callable]]] = ContextVar('_context_stack', default=[])


def _resolve_function(func: Callable) -> Callable:
    """Walk context stack from top to bottom, return first override found."""
    stack = _context_stack.get()
    for overrides in reversed(stack):
        if func in overrides:
            return overrides[func]
    return func


class context:
    def __init__(self, overrides: dict[Callable, Callable]):
        self.overrides = overrides
        self.token = None

    def __enter__(self):
        stack = _context_stack.get().copy()
        stack.append(self.overrides)
        self.token = _context_stack.set(stack)
        return self

    def __exit__(self, *args):
        _context_stack.reset(self.token)

    async def __aenter__(self):
        stack = _context_stack.get().copy()
        stack.append(self.overrides)
        self.token = _context_stack.set(stack)
        return self

    async def __aexit__(self, *args):
        _context_stack.reset(self.token)


def dep(
    cached: bool = False,
    cache_key_func: Callable[..., str] = lambda *args, **kwargs: json.dumps(
        {"args": args, "kwargs": kwargs},
        sort_keys=True,
        default=str,
    ),
) -> Callable[
    [Union[Callable[..., Generator[T, None, None]], Callable[..., AsyncGenerator[T, None]]]],
    Union[Callable[..., contextmanager[T]], Callable[..., asynccontextmanager[T]]],
]:
    """
    Decorator for defining dependencies.

    Args:
        cached: If True, the result will be cached and reused for the duration of the context
        cache_key_func: Function to generate cache keys from arguments. Defaults to JSON serialization with sorted keys.
    """

    def decorator(func: Callable[..., Generator[T, None, None]]) -> Callable[..., contextmanager[T]]:
        @wraps(func)
        @contextmanager
        def sync_wrapper(*args, **kwargs) -> Generator[T, None, None]:
            # - Resolve target function

            target_func = _resolve_function(func)

            # - Build cache key

            cache_key = f"{id(target_func)}:{cache_key_func(*args, **kwargs)}"

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

            # - Store in cache before yielding

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
                finally:
                    # - Remove from cache after cleanup (always runs, even on exception)

                    if cached:
                        _cache.pop(cache_key, None)

        @wraps(func)
        @asynccontextmanager
        async def async_wrapper(*args, **kwargs) -> AsyncGenerator[T, None]:
            # - Resolve target function

            target_func = _resolve_function(func)

            # - Build cache key

            cache_key = f"{id(target_func)}:{cache_key_func(*args, **kwargs)}"

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

            # - Store in cache before yielding

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
                finally:
                    # - Remove from cache after cleanup (always runs, even on exception)

                    if cached:
                        _cache.pop(cache_key, None)

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

    # - Test context override

    async def test_async_context():
        @dep()
        async def get_bar():
            yield "original"

        async def new_get_bar():
            yield "overridden"

        async with context({get_bar: new_get_bar}):
            async with get_bar() as value:
                assert value == "overridden"

        async with get_bar() as value:
            assert value == "original"

    asyncio.run(test_async_context())


if __name__ == "__main__":
    test()
