from database import db

col = db["admins"] if db is not None else None


async def add_admin(uid):
    if col is None: return False
    await col.update_one({"user_id": uid}, {"$set": {"user_id": uid}}, upsert=True)
    return True


async def remove_admin(uid):
    if col is None: return False
    r = await col.delete_one({"user_id": uid})
    return r.deleted_count > 0


async def list_admins():
    if col is None: return []
    try:
        return [d["user_id"] async for d in col.find()]
    except Exception:
        return []


async def is_admin(uid):
    if col is None: return False
    return bool(await col.find_one({"user_id": uid}))
