"""Apex Spam X — per-client dedup. EVERY bot responds independently."""
import logging
import time

log = logging.getLogger("ApexSpam.dedup")

_seen = {}
_WINDOW = 3.0
_patched = False


def _prune(now):
    for k in [k for k, t in _seen.items() if now - t > _WINDOW]:
        _seen.pop(k, None)


def is_dup(key):
    now = time.time()
    _prune(now)
    if key in _seen:
        return True
    _seen[key] = now
    return False


def clear():
    _seen.clear()


def patch():
    """Dedup per (bot, chat, msg, handler). All bots fire independently."""
    global _patched
    if _patched:
        return True
    try:
        from telethon import TelegramClient

        orig_on = TelegramClient.on

        def patched_on(self, event, *args, **kwargs):
            def deco(fn):
                hname = getattr(fn, "__name__", "h")

                async def wrapper(e):
                    try:
                        cid = getattr(e, "chat_id", None)
                        mid = getattr(e, "id", None)
                        if cid is not None and mid is not None:
                            key = (id(self), cid, mid, hname)
                            if is_dup(key):
                                return
                    except Exception:
                        pass
                    try:
                        return await fn(e)
                    except Exception as ex:
                        log.exception(f"handler {hname} failed: {ex}")

                wrapper.__name__ = hname
                return orig_on(self, event, *args, **kwargs)(wrapper)
            return deco

        TelegramClient.on = patched_on
        _patched = True
        log.info("✅ dedup (per-client, all bots respond)")
        return True
    except Exception as e:
        log.exception(f"dedup patch failed: {e}")
        return False
