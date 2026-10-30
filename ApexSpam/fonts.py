"""Apex Spam X — font engine (markdown/HTML safe) + global patcher."""
import logging
import re

log = logging.getLogger("ApexSpam.fonts")

_UP = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_LO = "abcdefghijklmnopqrstuvwxyz"
_DG = "0123456789"
_SMALL = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"


def _map(start, chars):
    return {c: chr(start + i) for i, c in enumerate(chars)}


_STYLED_RANGES = [
    (0x1D400, 0x1D419, 'A'),  # bold A-Z
    (0x1D41A, 0x1D433, 'a'),  # bold a-z
    (0x1D434, 0x1D44D, 'A'),  # italic A-Z
    (0x1D44E, 0x1D467, 'a'),  # italic a-z
    (0x1D468, 0x1D481, 'A'),  # bold italic A-Z
    (0x1D482, 0x1D49B, 'a'),  # bold italic a-z
    (0x1D4D0, 0x1D4E9, 'A'),  # script A-Z
    (0x1D4EA, 0x1D503, 'a'),  # script a-z
    (0x1D538, 0x1D551, 'A'),  # double-struck A-Z
    (0x1D552, 0x1D56B, 'a'),  # double-struck a-z
    (0x1D5A0, 0x1D5B9, 'A'),  # sans-serif A-Z
    (0x1D5BA, 0x1D5D3, 'a'),  # sans-serif a-z
    (0x1D670, 0x1D689, 'A'),  # mono A-Z
    (0x1D68A, 0x1D6A3, 'a'),  # mono a-z
]

_SMALL_CAPS = {
    'ᴀ':'A','ʙ':'B','ᴄ':'C','ᴅ':'D','ᴇ':'E','ꜰ':'F','ɢ':'G','ʜ':'H',
    'ɪ':'I','ᴊ':'J','ᴋ':'K','ʟ':'L','ᴍ':'M','ɴ':'N','ᴏ':'O','ᴘ':'P',
    'ǫ':'Q','ʀ':'R','ꜱ':'S','ᴛ':'T','ᴜ':'U','ᴠ':'V','ᴡ':'W','x':'x',
    'ʏ':'Y','ᴢ':'Z',
}


def asciify(text):
    """Strip styled Unicode back to plain ASCII so fonts can re-style."""
    if not text:
        return text
    out = []
    for ch in text:
        if ch in _SMALL_CAPS:
            out.append(_SMALL_CAPS[ch])
            continue
        cp = ord(ch)
        mapped = None
        for start, end, base in _STYLED_RANGES:
            if start <= cp <= end:
                mapped = chr(ord(base) + (cp - start))
                break
        out.append(mapped if mapped else ch)
    return "".join(out)


_FONTS = {
    "normal": {},
    "bold": {**_map(0x1D400, _UP), **_map(0x1D41A, _LO), **_map(0x1D7CE, _DG)},
    "italic": {
        **_map(0x1D434, _UP),
        **_map(0x1D44E, _LO[:7]),
        "h": "\u210E",
        **_map(0x1D456, _LO[8:]),
    },
    "script": {**_map(0x1D4D0, _UP), **_map(0x1D4EA, _LO)},
    "small": dict(zip(_UP + _LO, _SMALL + _SMALL)),
    "mono": {**_map(0x1D670, _UP), **_map(0x1D68A, _LO), **_map(0x1D7F6, _DG)},
}

FONT_ORDER = ["normal", "bold", "italic", "script", "small", "mono"]
FONT_INDEX = {i: n for i, n in enumerate(FONT_ORDER)}
FONT_LABELS = {
    "normal": "Normal", "bold": "Bold", "italic": "Italic",
    "script": "Script", "small": "Small", "mono": "Mono",
}
ACTIVE_FONT = "normal"

try:
    _PROTECT = re.compile(
        r"```[\s\S]*?```"
        r"|<code>[\s\S]*?</code>"
        r"|<a\s[^>]*>[\s\S]*?</a>"
        r"|`[^`]*`"
        r"|\[[^\]\n]*\]\([^)\n]+\)"
        r"|https?://\S+|tg://\S+"
        r"|<[^>]+>"
        r"|&[#a-zA-Z0-9]+;"
        r"|@[A-Za-z0-9_]{3,}"
    )
except re.error:  # ultra-safe fallback
    _PROTECT = re.compile(r"https?://\S+|tg://\S+|@[A-Za-z0-9_]{3,}")


def _tr(seg, table):
    return "".join(table.get(c, c) for c in seg)


def transform(text):
    if not text or ACTIVE_FONT == "normal":
        return text
    table = _FONTS.get(ACTIVE_FONT)
    if not table:
        return text
    text = asciify(text)
    out, last = [], 0
    for m in _PROTECT.finditer(text):
        out.append(_tr(text[last:m.start()], table))
        out.append(m.group())
        last = m.end()
    out.append(_tr(text[last:], table))
    return "".join(out)


def fx(text):
    return transform(text)


_patched = False
_orig = {}


def _tx(msg, kw):
    if isinstance(msg, str):
        msg = transform(msg)
    if isinstance(kw.get("caption"), str):
        kw["caption"] = transform(kw["caption"])
    return msg, kw


async def _p_send(self, entity, message=None, **kw):
    message, kw = _tx(message, kw)
    return await _orig["send"](self, entity, message, **kw)


async def _p_file(self, entity, file=None, **kw):
    _, kw = _tx(None, kw)
    return await _orig["file"](self, entity, file, **kw)


async def _p_edit(self, entity, mid, text=None, **kw):
    if isinstance(text, str):
        text = transform(text)
    if isinstance(kw.get("caption"), str):
        kw["caption"] = transform(kw["caption"])
    return await _orig["edit"](self, entity, mid, text, **kw)


async def _p_reply(self, message=None, **kw):
    message, kw = _tx(message, kw)
    return await _orig["reply"](self, message, **kw)


async def _p_respond(self, message=None, **kw):
    message, kw = _tx(message, kw)
    return await _orig["respond"](self, message, **kw)


async def _p_msg_edit(self, text=None, **kw):
    if isinstance(text, str):
        text = transform(text)
    return await _orig["msg_edit"](self, text, **kw)


def patch():
    global _patched
    if _patched:
        return True
    try:
        from telethon import TelegramClient
        from telethon.tl.custom.message import Message

        _orig["send"] = TelegramClient.send_message
        _orig["file"] = TelegramClient.send_file
        _orig["edit"] = TelegramClient.edit_message
        _orig["reply"] = Message.reply
        _orig["respond"] = Message.respond
        _orig["msg_edit"] = Message.edit

        TelegramClient.send_message = _p_send
        TelegramClient.send_file = _p_file
        TelegramClient.edit_message = _p_edit
        Message.reply = _p_reply
        Message.respond = _p_respond
        Message.edit = _p_msg_edit
        _patched = True
        log.info("font patcher installed")
    except Exception as e:
        log.exception(f"font patch failed: {e}")
    return _patched


async def send_raw(client, *a, **kw):
    return await _orig["send"](client, *a, **kw)


async def edit_raw(client, *a, **kw):
    try:
        return await _orig["edit"](client, *a, **kw)
    except Exception as e:
        if "NotModified" in type(e).__name__:
            return None
        raise


async def set_font(name):
    global ACTIVE_FONT
    if name not in _FONTS:
        return False
    ACTIVE_FONT = name
    try:
        from models.bot_settings import set_value
        await set_value("active_font", name)
    except Exception:
        pass
    return True


async def sync_from_db():
    global ACTIVE_FONT
    try:
        from models.bot_settings import get_value
        name = await get_value("active_font")
        if name in _FONTS and name != ACTIVE_FONT:
            ACTIVE_FONT = name
            log.info(f"font synced: {name}")
    except Exception:
        pass
