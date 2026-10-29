from database import db
import config

sudo_col = db["sudo_users"]

async def add_sudo(uid, added_by=0):
    await sudo_col.update_one(
        {"user_id": uid},
        {"$set": {"user_id": uid, "added_by": added_by}},
        upsert=True,
    )
    if uid not in config.SUDO_USERS:
        config.SUDO_USERS.append(uid)

async def remove_sudo(uid):
    res = await sudo_col.delete_one({"user_id": uid})
    if uid in config.SUDO_USERS:
        config.SUDO_USERS.remove(uid)
    return res.deleted_count > 0

async def mongo_ids():
    return [d["user_id"] async for d in sudo_col.find()]

async def is_sudo(uid):
    if uid == config.OWNER_ID:
        return True
    if uid in config.SUDO_USERS:
        return True
    return bool(await sudo_col.find_one({"user_id": uid}))
