"""Apex Spam X — Telegram rich button styles (string, not object!)."""
import logging
from telethon import Button

log = logging.getLogger("ApexSpam.buttons")
HAS_STYLE = True
_VALID = ("primary", "danger", "success")


def _k(kind):
    return kind if kind in _VALID else "primary"


def ib(text, data, kind="primary"):
    """Inline callback button with colour: primary|danger|success."""
    try:
        return Button.inline(text, data, style=_k(kind))
    except TypeError:
        global HAS_STYLE
        HAS_STYLE = False
        return Button.inline(text, data)


def ub(text, url, kind="primary"):
    """URL button with colour."""
    try:
        return Button.url(text, url, style=_k(kind))
    except TypeError:
        return Button.url(text, url)
