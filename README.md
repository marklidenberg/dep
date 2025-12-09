# dep

Python dependency injection using context managers.

## Installation

```bash
pip install "git+https://github.com/marklidenberg/dep.git"
```

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

```python
from dep import dep

@dep(cached=True)
def get_session_db(env: str):
    ...

with get_session_db(env='test') as db:
    # separate cache for each environment
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
