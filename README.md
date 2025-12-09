# dep

Lightweight dependency injection for Python.

## Usage

```python
from dep import dep, context

# - Define dependencies

@dep(cached=True)
async def get_db():
    db = Database()
    yield db
    db.close()

async with get_db() as db:
    ...

# - Override with context

@dep()
def get_mock_db():
    yield MockDatabase()

async with context({get_db: get_mock_db}):
    async with get_db() as db:
        ...
```


## Recipe: argument-scoped caching

If you need separate cache instances, pass the scope info in as function arguments.

```python
from dep import dep

@dep(cached=True)
def get_session_db(env: str):
    ...

with get_session_db(env='test') as db:
    ...
```

## Cache Lifetime

When `cached=True`, the dependency is cached and reused across multiple context manager calls. The cache entry is removed after the first context call exits and cleanup runs:

```python
@dep(cached=True)
def get_db():
    db = Database()
    yield db
    db.close()  # Cleanup runs after context exits

# First call: creates and caches
with get_db() as db:
    with get_db() as db2:
        ... # uses the cached value

# Cache is cleared after context exits and cleanup runs
```

Cached dependencies are stored per-container and keyed by function + arguments.

## API Reference

```python
def dep(
    cached: bool = False,
    cache_key_func = lambda *args, **kwargs: json.dumps(
        {"args": args, "kwargs": kwargs},
        sort_keys=True,
        default=str
    ),
):
    """
    Decorator for defining dependencies.

    Args:
        cached: If True, the result will be cached and reused for the duration of the context
        cache_key_func: Function to generate cache keys from arguments.
                        Defaults to JSON serialization with sorted keys (sort_keys=True, default=str)
    """
    ...

class context:
    """Context manager to scope dependencies"""
    def __init__(self, overrides: dict[Callable, Callable]): ...

class Container:
    """
    Dependency injection container.

    By default, `dep` and `context` use a shared global container. Create separate containers for isolation (e.g., testing, multi-tenancy)
    """
    def dep(self, cached: bool = False, cache_key_func = ...): ...
    def context(self, overrides: dict[Callable, Callable]): ...
```

## Notes

- Works with both sync and async functions
- Context is managed with `contextvars` - safe for async/await