# dep

Remarkably simple Python dependency injection

## Usage

```python
from dep import dep, override

# - Basic example

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

# - Override for testing

@dep()
def get_mock_db():
    yield MockDatabase()

override(get_db=get_mock_db)
```
