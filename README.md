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

## Recipe: Scopes

Use the `scope` parameter to manage different scopes (session, thread, environment, etc.) for cached dependencies. The `scope` is a function parameter (not a `@dep` parameter) that defaults to an empty tuple. Dict values are automatically converted to sorted tuples for proper caching.

```python
from dep import dep

# Session-scoped dependency
@dep(cached=True)
def get_session_db(scope=("session",)):
    db = Database(session_id=get_current_session())
    yield db
    db.close()

# Thread-scoped dependency
@dep(cached=True)
def get_thread_cache(scope=("thread",)):
    cache = ThreadLocalCache()
    yield cache
    cache.clear()

# Environment-scoped dependency
@dep(cached=True)
def get_prod_config(scope={"env": "production"}):
    config = Config(env="production")
    yield config

# Different scopes maintain separate cached instances
def process_request():
    with get_session_db() as db:  # Cached per session
        with get_thread_cache() as cache:  # Cached per thread
            # Process using scoped resources
            pass
```
