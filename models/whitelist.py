from database import db

col = db["whitelist_gcs"] if db is not None else None


async def add_gc(chat_id):
    if col is None: return False
    await col.update_one({"chat_id": chat_id}, {"$set": {"chat_id": chat_id}}, upsert=True)
    return True


async def remove_gc(chat_id):
    if col is None: return False
    r = await col.delete_one({"chat_id": chat_id})
    return r.deleted_count > 0


async def list_gcs():
    if col is None: return []
    try:
        return [d["chat_id"] async for d in col.find()]
    except Exception:
        return []


async def is_whitelisted(chat_id):
    if col is None: return False
    return bool(await col.find_one({"chat_id": chat_id}))
