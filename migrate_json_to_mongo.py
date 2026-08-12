"""
One-time migration: import the old local data.json into MongoDB Atlas.

Run from the backend_app folder:
    python migrate_json_to_mongo.py [--force]

Reads data.json / accounts.json / sessions.json (the old local storage) and
writes them into the MongoDB collections defined in db.py.

The cloud already contains your place data in MyTraveldata.Data, so this
script SKIPS the places step unless you pass --force to overwrite it.
"""

import json
import os
import sys

from db import data_collection, accounts_collection, sessions_collection


def migrate_data(force: bool):
    if not os.path.exists("data.json"):
        print("data.json not found - skipping places")
        return
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    existing = data_collection.count_documents({})
    if existing and not force:
        print(
            f"MyTraveldata.Data already has {existing} document(s) - skipping. "
            "Use --force to overwrite with the local data.json."
        )
        return
    data_collection.update_one({}, {"$set": data}, upsert=True)
    n = len(data.get("data", {}).get("data", []))
    print(f"Places document migrated: {n} places")


def migrate_accounts():
    if not os.path.exists("accounts.json"):
        print("accounts.json not found - skipping accounts")
        return
    with open("accounts.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    users = data.get("users", [])
    for user in users:
        existing = accounts_collection.find_one({"username": user.get("username")})
        if not existing:
            accounts_collection.insert_one(user)
    print(f"Accounts migrated: {len(users)}")


def migrate_sessions():
    if not os.path.exists("sessions.json"):
        print("sessions.json not found - skipping sessions")
        return
    with open("sessions.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    items = data.get("sessions", [])
    for session in items:
        existing = sessions_collection.find_one({"session_id": session.get("session_id")})
        if not existing:
            sessions_collection.insert_one(session)
    print(f"Sessions migrated: {len(items)}")


if __name__ == "__main__":
    force = "--force" in sys.argv
    print("Migrating local JSON files to MongoDB...")
    migrate_data(force)
    migrate_accounts()
    migrate_sessions()
    print("Migration finished.")
