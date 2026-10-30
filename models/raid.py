from database import db
from ApexSpam import cache

raid_col = db["raid_messages"] if db is not None else None
_TTL = 300


async def get_raid_messages(category):
    if raid_col is None:
        return []
    key = ("raid", category)
    hit = cache.get(key)
    if hit is not None:
        return hit
    try:
        doc = await raid_col.find_one({"category": category})
        msgs = doc.get("messages", []) if doc else []
    except Exception:
        msgs = []
    cache.set(key, msgs, _TTL)
    return msgs


async def set_raid_messages(category, messages):
    if raid_col is None:
        return False
    await raid_col.update_one(
        {"category": category}, {"$set": {"messages": messages}}, upsert=True
    )
    cache.drop(("raid", category))
    return True
