from database import db

settings_col = db["settings"]

async def get_setting(key: str, default=None):
    doc = await settings_col.find_one({"_id": key})
    return doc["value"] if doc else default

async def set_setting(key: str, value):
    await settings_col.update_one(
        {"_id": key}, {"$set": {"value": value}}, upsert=True
    )
