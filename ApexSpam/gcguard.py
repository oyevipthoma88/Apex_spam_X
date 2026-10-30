"""Apex Spam X — auto GC admin warning."""
import logging

log = logging.getLogger("ApexSpam.gcguard")

_cache = {}


async def is_bot_admin(client, chat_id):
    key = (id(client), chat_id)
    if key in _cache:
        return _cache[key]
    try:
        me = await client.get_me()
        perms = await client.get_permissions(chat_id, me.id)
        result = bool(getattr(perms, "is_admin", False))
    except Exception:
        result = True  # can't check → assume OK (DM/unknown)
    _cache[key] = result
    return result


async def warn_if_not_admin(client, chat_id, is_private):
    """Returns warning text (HTML) if bot is NOT admin in this GC."""
    if is_private:
        return ""
    if await is_bot_admin(client, chat_id):
        return ""
    return (
        "\n\n<blockquote>⚠️ <b>Bot is not admin</b>\n"
        "Some commands may not respond. Run <code>.gcsetup</code> for fix.</blockquote>"
    )


def clear_cache():
    _cache.clear()
