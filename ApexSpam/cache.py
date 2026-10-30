"""Apex Spam X — tiny TTL cache for hot paths."""
import time

_data = {}


def get(key):
    item = _data.get(key)
    if not item:
        return None
    val, exp = item
    if exp and time.time() > exp:
        _data.pop(key, None)
        return None
    return val


def set(key, val, ttl=300):
    _data[key] = (val, time.time() + ttl if ttl else 0)


def drop(*keys):
    for k in keys:
        _data.pop(k, None)


def drop_prefix(prefix):
    for k in [k for k in _data if str(k).startswith(str(prefix))]:
        _data.pop(k, None)


def clear():
    _data.clear()
