import time
from database import db

users_col = db["users"]

async def track_user(uid: int, username: str | None = None):
    now = int(time.time())
    await users_col.update_one(
        {"user_id": uid},
        {
            "$set": {"username": username, "last_seen": now},
            "$setOnInsert": {"first_seen": now},
        },
        upsert=True,
    )
