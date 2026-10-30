from database import db
import config

sudo_col = db["sudo_users"] if db is not None else None


async def add_sudo(uid, added_by=0):
    if sudo_col is None:
        return False
    await sudo_col.update_one(
        {"user_id": uid},
        {"$set": {"user_id": uid, "added_by": added_by}},
        upsert=True,
    )
    if uid not in config.SUDO_USERS:
        config.SUDO_USERS.append(uid)
    return True


async def remove_sudo(uid):
    if sudo_col is None:
        return False
    res = await sudo_col.delete_one({"user_id": uid})
    if uid in config.SUDO_USERS:
        config.SUDO_USERS.remove(uid)
    return res.deleted_count > 0


async def mongo_ids():
    if sudo_col is None:
        return []
    try:
        return [d["user_id"] async for d in sudo_col.find()]
    except Exception:
        return []


async def is_sudo(uid):
    if uid == config.OWNER_ID:
        return True
    if uid in config.SUDO_USERS:
        return True
    if sudo_col is None:
        return False
    try:
        return bool(await sudo_col.find_one({"user_id": uid}))
    except Exception:
        return False
