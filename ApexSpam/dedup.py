"""Apex Spam X — global dedup (1 response per command across ALL bots)."""
import logging
import time

log = logging.getLogger("ApexSpam.dedup")

_seen = {}
_WINDOW = 5.0
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


def _primary_client():
    try:
        from ApexSpam import CLIENTS
        return CLIENTS[0] if CLIENTS else None
    except Exception:
        return None


def patch():
    """Global dedup + non-primary skips group messages (all DMs still work)."""
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
                        # skip non-primary in groups (avoids 10x duplicate)
                        if not getattr(e, "is_private", True):
                            primary = _primary_client()
                            if primary is not None and self is not primary:
                                return
                        # global dedup key (no client id)
                        cid = getattr(e, "chat_id", None)
                        mid = getattr(e, "id", None)
                        if cid is not None and mid is not None:
                            if is_dup((cid, mid, hname)):
                                return
                    except Exception:
                        pass
                    return await fn(e)

                wrapper.__name__ = hname
                return orig_on(self, event, *args, **kwargs)(wrapper)
            return deco

        TelegramClient.on = patched_on
        _patched = True
        log.info("✅ dedup (global, primary-in-groups)")
        return True
    except Exception as e:
        log.exception(f"dedup patch failed: {e}")
        return False
