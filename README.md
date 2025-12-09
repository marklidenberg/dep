# dep

Lightweight dependency injection for Python.

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

def override(mapping: dict[Callable, Callable]):
    """Override dependency functions with new implementations."""
    ...
```

## Usage

```python
from dep import dep, override

# - Example

@dep(cached=True)
async def get_db():
    db = Database()
    yield db
    db.close()

async def get_user(user_id: int):
    async with get_db() as db:
        if user := cache.get(user_id):
            return user
        user = db.query(user_id)
        cache.set(user_id, user)
        return user

# - Override

@dep()
def get_mock_db():
    yield MockDatabase()

override({get_db: get_mock_db})
```

## Recipe: scopes

Pass scope information as function arguments to create separate cache instances for different contexts (session, thread, environment, etc.).

```python
from dep import dep

@dep(cached=True)
def get_session_db(scope: dict):
    ...

with get_session_db(scope={'env': 'test'}) as db:
    ...
```


## Notes

- Works with both sync and async functions
- Cache keys are JSON-serialized inputs with sorted keys. You can override this with a custom key function if needed.
