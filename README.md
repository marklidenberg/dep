# dep

Lightweight dependency injection for Python.

## API Reference

```python
def dep(cached: bool = False):
    """Decorator for defining dependencies."""
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

@dep(cached=True)
async def get_cache():
    cache = Redis()
    yield cache
    cache.disconnect()

async def get_user(user_id: int):
    async with get_db() as db, get_cache() as cache:
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
- Top-level dict arguments are converted to sorted tuples when computing cache keys

