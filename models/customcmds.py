from database import db

col = db["user_commands"] if db is not None else None


async def set_cmd(user_id, cmd, response):
    if col is None:
        return False
    await col.update_one(
        {"_id": f"{user_id}:{cmd}"},
        {"$set": {"user_id": user_id, "cmd": cmd, "response": response}},
        upsert=True,
    )
    return True


async def del_cmd(user_id, cmd):
    if col is None:
        return False
    r = await col.delete_one({"_id": f"{user_id}:{cmd}"})
    return r.deleted_count > 0


async def list_cmds(user_id):
    if col is None:
        return []
    try:
        return [d async for d in col.find({"user_id": user_id})]
    except Exception:
        return []


async def load_all():
    if col is None:
        return {}
    out = {}
    try:
        async for d in col.find({}):
            out[(d["user_id"], d["cmd"].lower())] = d["response"]
    except Exception:
        pass
    return out
