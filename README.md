# dep

Lightweight dependency injection for Python.

## Usage

```python
from dep import dep, override

# - Example

@dep()
def foo():
    yield "bar"

with foo() as value:
    assert value == "bar"

# - Async support

@dep()
async def foo():
    yield "async_bar"

async with foo() as value:
    assert value == "async_bar"

# - Real-world example (with caching for expensive resources)

@dep(cached=True)
def get_db():
    db = Database()
    yield db
    db.close()

@dep(cached=True)
def get_cache():
    cache = Redis()
    yield cache
    cache.disconnect()

def get_user(user_id: int):
    with get_db() as db, get_cache() as cache:
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

## Notes

- Top-level dict args are converted to sorted tuples under the hood for caching

## Recipe: Scopes

Pass scope information as function arguments to create separate cache instances for different contexts (session, thread, environment, etc.). 

```python
from dep import dep

@dep(cached=True)
def get_session_db(scope: dict):
    ...

with get_session_db(scope={'env': 'test'}) as db:
    ...
```
