"""Apex Spam X — buttons with Bot API 9.4 styles + 7.11 copy buttons."""
import logging
from telethon import Button
from telethon.tl import types

log = logging.getLogger("ApexSpam.buttons")
HAS_STYLE = True


def ib(text, data, kind="primary", icon=None):
    try:
        return Button.inline(text, data, style=kind, icon=icon)
    except TypeError:
        return Button.inline(text, data)
    except Exception:
        return Button.inline(text, data)


def ub(text, url, kind="primary", icon=None):
    try:
        return Button.url(text, url, style=kind, icon=icon)
    except TypeError:
        return Button.url(text, url)
    except Exception:
        return Button.url(text, url)


def copy_btn(text, copy_text, kind="primary", icon=None):
    try:
        return types.KeyboardButtonCopy(text=text, copy_text=copy_text)
    except Exception:
        return None


def nav(back=b"back", close=True):
    row = [ib("« Back", back, "primary")]
    if close:
        row.append(ib("✖ Close", b"close", "danger"))
    return row


def grid(items, cols=2):
    rows, row = [], []
    for b in items:
        if b is None:
            continue
        row.append(b)
        if len(row) == cols:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return rows
