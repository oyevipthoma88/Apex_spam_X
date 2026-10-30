from database import db

settings = db["bot_settings"] if db is not None else None


async def set_value(key, value):
    if settings is None:
        return False
    await settings.update_one({"_id": key}, {"$set": {"value": value}}, upsert=True)
    return True


async def get_value(key, default=None):
    if settings is None:
        return default
    try:
        doc = await settings.find_one({"_id": key})
        return doc["value"] if doc else default
    except Exception:
        return default


async def del_value(key):
    if settings is None:
        return False
    res = await settings.delete_one({"_id": key})
    return res.deleted_count > 0
