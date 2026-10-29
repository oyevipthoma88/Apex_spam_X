from database import db

sudo_col = db["sudo_users"]

async def add_sudo(uid: int, added_by: int = 0):
    await sudo_col.update_one(
        {"user_id": uid},
        {"$set": {"user_id": uid, "added_by": added_by}},
        upsert=True,
    )

async def remove_sudo(uid: int) -> bool:
    res = await sudo_col.delete_one({"user_id": uid})
    return res.deleted_count > 0

async def is_sudo(uid: int) -> bool:
    return bool(await sudo_col.find_one({"user_id": uid}))

async def all_sudo() -> list[int]:
    return [doc["user_id"] async for doc in sudo_col.find()]
