"""
MongoDB storage layer for the backend app (MongoDB Atlas, via pymongo).

Storage layout in Atlas:
  database:    MyTraveldata
  collection:  Data      -> ONE document holding the whole place list:
                            {"data": {"data": [place, place, ...]}}
  collection:  accounts  -> one document per user
  collection:  sessions  -> one document per login session

The "Data" document keeps the exact same shape as the old data.json file,
so all API responses stay identical to before.

Driver: python -m pip install "pymongo[srv]"
"""

import asyncio
import copy
import os
import time

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

# Connection string (MongoDB Atlas). Override via MONGODB_URI in .env if needed.
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://samikshatechsolutions_db_user:Mangeeta_143@cluster0.zkvxset.mongodb.net/?appName=Cluster0",
)

DB_NAME = os.getenv("MONGODB_DB_NAME", "MyTraveldata")

# pymongo is a sync driver; the client connects lazily (no network call at import).
client = MongoClient(
    MONGODB_URI,
    server_api=ServerApi("1"),
    serverSelectionTimeoutMS=5000,
)
db = client[DB_NAME]

# One document in this collection holds the whole place list: {"data": {"data": [...]}}
data_collection = db["Data"]
accounts_collection = db["accounts"]
sessions_collection = db["sessions"]

EMPTY_DATA = {"data": {"data": []}}

# In-process cache so repeated / concurrent reads never hit Atlas more than
# once per TTL window. Every load_data() call returns a fresh deep copy, so
# callers can safely mutate the result without corrupting the cache, and every
# write (save_data) invalidates the cache immediately.
# Tune with the DATA_CACHE_TTL env var (seconds). Default: 60s.
DATA_CACHE_TTL = int(os.getenv("DATA_CACHE_TTL", "60"))

_data_cache = None
_data_cache_time = 0.0


def _invalidate_cache():
    global _data_cache, _data_cache_time
    _data_cache = None
    _data_cache_time = 0.0


async def _run(func, *args, **kwargs):
    """Run a blocking pymongo call in a worker thread so the event loop stays free."""
    return await asyncio.to_thread(func, *args, **kwargs)


async def init_indexes():
    """Create unique indexes. Non-fatal if it fails (e.g. duplicate old data)."""
    for collection, field in [
        (accounts_collection, "username"),
        (sessions_collection, "session_id"),
    ]:
        try:
            await _run(collection.create_index, field, unique=True)
        except Exception as e:
            print(f"WARNING: could not create unique index on {collection.name}.{field}: {e}")


async def close_db():
    await _run(client.close)


# ------------------------------------------------------------------
# places data (was: data.json) -> MyTraveldata.Data (single wrapper doc)
# ------------------------------------------------------------------
async def load_data():
    """Return {"data": {"data": [...]}} - same shape as the old data.json.

    Cached in-process for DATA_CACHE_TTL seconds; each call returns a fresh
    deep copy, so the result is always safe to mutate. Writes invalidate the
    cache, so newly added/edited places are visible immediately.
    """
    global _data_cache, _data_cache_time

    now = time.monotonic()
    if _data_cache is not None and (now - _data_cache_time) < DATA_CACHE_TTL:
        return copy.deepcopy(_data_cache)

    doc = await _run(data_collection.find_one, {})
    if not doc:
        doc = {"data": {"data": []}}
    else:
        doc.pop("_id", None)

    _data_cache = doc
    _data_cache_time = now
    return copy.deepcopy(doc)


async def save_data(data):
    """Replace the whole wrapper document (mirrors the old data.json rewrite)."""
    await _run(data_collection.update_one, {}, {"$set": data}, upsert=True)
    _invalidate_cache()
    return data


async def get_place(place_id: str):
    """Fetch a single place by its string id, or None."""
    data = await load_data()
    for entry in data.get("data", {}).get("data", []):
        if str(entry.get("id")) == str(place_id):
            return entry
    return None


async def add_place(entry: dict):
    """Append a new place to the list and save to Atlas."""
    data = await load_data()
    data.setdefault("data", {}).setdefault("data", []).append(entry)
    await save_data(data)
    return None


async def update_place(entry: dict):
    """Replace the place with the matching id (appends if missing)."""
    data = await load_data()
    entries = data.setdefault("data", {}).setdefault("data", [])
    for i, existing in enumerate(entries):
        if str(existing.get("id")) == str(entry.get("id")):
            entries[i] = entry
            break
    else:
        entries.append(entry)
    await save_data(data)
    return None


async def delete_place(place_id: str):
    """Remove the place with the matching id from the list."""
    data = await load_data()
    entries = data.get("data", {}).get("data", [])
    data["data"]["data"] = [e for e in entries if str(e.get("id")) != str(place_id)]
    await save_data(data)
    return None


# ------------------------------------------------------------------
# accounts (was: accounts.json) -> MyTraveldata.accounts
# ------------------------------------------------------------------
async def load_accounts():
    """Return {"users": [...]} - same shape as the old accounts.json."""
    users = await _run(lambda: list(accounts_collection.find({})))
    for u in users:
        u.pop("_id", None)
    return {"users": users}


async def add_account(user_doc: dict):
    """Insert a new user document."""
    return await _run(accounts_collection.insert_one, user_doc)


# ------------------------------------------------------------------
# sessions (was: sessions.json) -> MyTraveldata.sessions
# ------------------------------------------------------------------
async def load_sessions():
    """Return {"sessions": [...]} - same shape as the old sessions.json."""
    items = await _run(lambda: list(sessions_collection.find({})))
    for s in items:
        s.pop("_id", None)
    return {"sessions": items}


async def find_session(session_id: str):
    """Fetch a single session by session_id, or None."""
    return await _run(sessions_collection.find_one, {"session_id": session_id})


async def create_session(session_doc: dict):
    """Insert a new session document."""
    return await _run(sessions_collection.insert_one, session_doc)
