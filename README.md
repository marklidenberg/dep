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
```


## Notes

- Works with both sync and async functions
- Context is managed with `contextvars` - safe for async/await