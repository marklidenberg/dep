from functools import wraps
from typing import Any, Callable, TypeVar
import asyncio
import inspect

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
                return _SyncContextManager(_cache[cache_key])

            # - Execute function and get result

            result_gen = target_func(*args, **kwargs)

            # - Extract yielded value

            try:
                result = next(result_gen)

                if cached:
                    _cache[cache_key] = result

                return _SyncContextManager(result, result_gen)

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
                return _AsyncContextManager(_cache[cache_key])

            # - Execute function and get result

            result_gen = target_func(*args, **kwargs)

            # - Extract yielded value

            try:
                result = await result_gen.__anext__()

                if cached:
                    _cache[cache_key] = result

                return _AsyncContextManager(result, result_gen)

            except StopAsyncIteration:
                raise RuntimeError(f"{func.__name__} did not yield a value")

        # - Determine wrapper type based on function type

        if asyncio.iscoroutinefunction(func) or inspect.isasyncgenfunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class _SyncContextManager:
    """Context manager for sync dependencies"""

    def __init__(self, value, generator=None):
        self.value = value
        self.generator = generator

    def __enter__(self):
        return self.value

    def __exit__(self, exc_type, exc_val, exc_tb):

        # - Clean up generator if present

        if self.generator:
            try:
                next(self.generator)
            except StopIteration:
                pass

        return False


class _AsyncContextManager:
    """Context manager for async dependencies"""

    def __init__(self, value, generator=None):
        self.value = value
        self.generator = generator

    async def __aenter__(self):
        return self.value

    async def __aexit__(self, exc_type, exc_val, exc_tb):

        # - Clean up generator if present

        if self.generator:
            try:
                await self.generator.__anext__()
            except StopAsyncIteration:
                pass

        return False
