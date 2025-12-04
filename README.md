# dep

Embarassingly simple Python dependency injection.

## Usage

```python
from dep import dep, override

# - Basic example 

@dep()
def get_db():
    db = Database()
    yield db
    db.close()

with get_db() as db:
    db.query(...)

# - Async support

@dep()
async def get_async_db():
    db = await AsyncDatabase()
    yield db
    await db.close()

async with get_async_db() as db:
    await db.query(...)

# - Real-world example

@dep()
def get_db():
    db = Database()
    yield db
    db.close()

@dep()
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

override({get_db: get_mock_db})
```
