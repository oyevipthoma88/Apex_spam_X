from database import db
from ApexSpam import cache
import time

col = db["chat_log"] if db is not None else None


async def mark_seen(chat_id, chat_title, is_private, bot_username):
    if col is None:
        return False
    ck = ("seen", str(chat_id))
    if cache.get(ck):
        return False
    try:
        existing = await col.find_one({"_id": str(chat_id)})
        if existing:
            cache.set(ck, True, 0)
            return False
        await col.insert_one({
            "_id": str(chat_id),
            "chat_id": chat_id,
            "chat_title": chat_title,
            "is_private": is_private,
            "first_bot": bot_username,
            "first_seen": int(time.time()),
        })
        cache.set(ck, True, 0)
        return True
    except Exception:
        return False
