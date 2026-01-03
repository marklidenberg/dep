# context-dep

Python dependency injection with minimal API using context managers. 

Use it in any codebase (including FastAPI) to provide configs, clients, DB sessions, loggers, etc. 

Instead of passing the same arguments through every function, your code can grab it when needed — it’s reused for the duration of the work, cleaned up afterward, and easy to replace with fakes in tests from one place.

```bash
pip install context-dep
```

## Basic usage

```python
from context_dep import dep, context


@dep(cached=True)
def get_db():
    db = Database()
    yield db
    db.close()

def my_func():
    with get_db() as db:
        ...
```

## Overrides

```
@dep()
def get_mock_db():
    yield MockDatabase()

def main():
    with context({get_db: get_mock_db}):
        my_func()

```

## Recipe: argument-scoped caching

```python
from context_dep import dep

@dep(cached=True)
def get_session_db(env: str):
    ...

with get_session_db(env='test') as db:
    # separate cache for each environment
    ...
```

## Recipe: stub dependency for later injection

```python
@dep()
async def get_db():
    raise NotImplementedError

async with get_db() as db:
    ...

```

## Cache Lifetime

When `cached=True`, the dependency is reused within nested calls and cleaned up once:

```python
@dep(cached=True)
def get_db():
    db = Database()
    yield db
    db.close()

with get_db() as db:
    with get_db() as db2:  # Reuses the same instance
        assert db is db2
# Cleanup runs once when the outermost context exits
```

## Notes

- Works with both sync and async functions
- Context is managed with `contextvars` - safe for async/await

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
        cached: If True, the dependency is reused within nested calls
        cache_key_func: Function to generate cache keys from arguments.
                        Defaults to JSON serialization with sorted keys (sort_keys=True, default=str)
    """
    ...

class context:
    """Context manager to scope dependencies"""
    def __init__(self, overrides: dict[Callable, Callable]): ...

class Container:
    """
    Dependency injection container, stores the cache and overrides

    By default, `dep` and `context` use a shared global container. 
    Create separate containers for isolation (e.g., testing, multi-tenancy)
    """
    def dep(self, cached: bool = False, cache_key_func = ...): ...
    def context(self, overrides: dict[Callable, Callable]): ...
```

## License

MIT License

## Author

Mark Lidenberg [marklidenberg@gmail.com](mailto:marklidenberg@gmail.com)
