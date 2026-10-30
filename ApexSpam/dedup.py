"""Apex Spam X — per-message dedup so 2 bots in one chat → 1 response."""
import time

_seen = {}
_WINDOW = 3.0


def is_dup(chat_id, msg_id):
    key = (chat_id, msg_id)
    now = time.time()
    # prune old
    for k in [k for k, t in _seen.items() if now - t > _WINDOW]:
        _seen.pop(k, None)
    if key in _seen:
        return True
    _seen[key] = now
    return False


def clear():
    _seen.clear()
