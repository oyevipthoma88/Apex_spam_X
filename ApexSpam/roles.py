"""Apex Spam X — role engine: owner > sudo > admin > user."""
import time
import config
from models.sudo import is_sudo, get_sudo
from models.admins import is_admin

OWNER, SUDO, ADMIN, USER = "owner", "sudo", "admin", "user"
_TTL = 20
_cache = {}


def invalidate(uid=None):
    if uid is None:
        _cache.clear()
    else:
        _cache.pop(uid, None)


async def role(uid: int) -> str:
    if uid == config.OWNER_ID:
        return OWNER
    now = time.time()
    hit = _cache.get(uid)
    if hit and now - hit[1] < _TTL:
        return hit[0]
    r = USER
    try:
        if await is_sudo(uid):
            r = SUDO
        elif await is_admin(uid):
            r = ADMIN
    except Exception:
        pass
    _cache[uid] = (r, now)
    return r


async def can_use(uid):
    return await role(uid) in (OWNER, SUDO, ADMIN)


async def can_moderate(uid):
    return await role(uid) in (OWNER, SUDO)


async def can_add_sudo(actor, target):
    r = await role(actor)
    if r == OWNER:
        if target == config.OWNER_ID:
            return False, "Owner already has full access."
        return True, ""
    if r != SUDO:
        return False, "Sudo / Owner only."
    if target == config.OWNER_ID:
        return False, "Cannot add owner."
    if await is_sudo(target):
        return False, "Already a sudo user."
    return True, ""


async def can_del_sudo(actor, target):
    r = await role(actor)
    if target == config.OWNER_ID:
        return False, "Cannot remove owner."
    if r == OWNER:
        return True, ""
    if r != SUDO:
        return False, "Sudo / Owner only."
    rec = await get_sudo(target)
    if not rec:
        return False, "Not a sudo user."
    if rec.get("source") == "env":
        return False, "Env sudo — only owner can remove."
    if rec.get("added_by") != actor:
        return False, "You can only remove users you added."
    return True, ""
