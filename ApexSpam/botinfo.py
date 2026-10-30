"""Apex Spam X — cached bot usernames (avoid get_me on every command)."""
from ApexSpam import cache


async def username(client):
    key = ("un", id(client))
    v = cache.get(key)
    if v:
        return v
    me = await client.get_me()
    v = me.username or "bot"
    cache.set(key, v, 0)          # permanent while process runs
    return v


async def warm(clients):
    for c in clients:
        try:
            await username(c)
        except Exception:
            pass
