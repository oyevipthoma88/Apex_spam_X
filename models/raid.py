from database import db

raid_col = db["raid_messages"]

async def get_raid_messages(category: str) -> list[str]:
    doc = await raid_col.find_one({"category": category})
    return doc.get("messages", []) if doc else []

async def set_raid_messages(category: str, messages: list[str]):
    await raid_col.update_one(
        {"category": category},
        {"$set": {"messages": messages}},
        upsert=True,
    )
