from database import db
from ApexSpam import cache

settings = db["bot_settings"] if db is not None else None
_TTL = 30


async def set_value(key, value):
    if settings is None:
        return False
    await settings.update_one({"_id": key}, {"$set": {"value": value}}, upsert=True)
    cache.drop(("set", key))
    return True


async def get_value(key, default=None):
    if settings is None:
        return default
    ck = ("set", key)
    hit = cache.get(ck)
    if hit is not None:
        return hit
    try:
        doc = await settings.find_one({"_id": key})
        val = doc["value"] if doc else default
    except Exception:
        val = default
    cache.set(ck, val, _TTL)
    return val


async def del_value(key):
    if settings is None:
        return False
    res = await settings.delete_one({"_id": key})
    cache.drop(("set", key))
    return res.deleted_count > 0
