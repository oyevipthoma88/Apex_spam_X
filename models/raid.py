from database import db

raid_col = db["raid_messages"] if db is not None else None


async def get_raid_messages(category):
    if raid_col is None:
        return []
    try:
        doc = await raid_col.find_one({"category": category})
        return doc.get("messages", []) if doc else []
    except Exception:
        return []


async def set_raid_messages(category, messages):
    if raid_col is None:
        return False
    await raid_col.update_one(
        {"category": category},
        {"$set": {"messages": messages}},
        upsert=True,
    )
    return True
