"""Apex Spam X — Telegram rich button styles with fallback."""
import logging
from telethon import Button
from telethon.tl import types

log = logging.getLogger("ApexSpam.buttons")

_STYLE = getattr(types, "KeyboardButtonStyle", None)
HAS_STYLE = _STYLE is not None
log.info(f"Rich buttons: {HAS_STYLE}")


def _st(kind):
    if not _STYLE:
        return None
    try:
        if kind == "danger":
            return _STYLE(bg_danger=True)
        if kind == "success":
            return _STYLE(bg_success=True)
        return _STYLE(bg_primary=True)
    except Exception:
        return None


def ib(text, data, kind="primary"):
    st = _st(kind)
    if st:
        try:
            return Button.inline(text, data, style=st)
        except TypeError:
            pass
    return Button.inline(text, data)


def ub(text, url, kind="primary"):
    st = _st(kind)
    if st:
        try:
            return Button.url(text, url, style=st)
        except TypeError:
            pass
    return Button.url(text, url)
