from database import db

settings = db["bot_settings"]


async def set_value(key: str, value):
    await settings.update_one({"_id": key}, {"$set": {"value": value}}, upsert=True)


async def get_value(key: str, default=None):
    doc = await settings.find_one({"_id": key})
    return doc["value"] if doc else default


async def del_value(key: str):
    res = await settings.delete_one({"_id": key})
    return res.deleted_count > 0
