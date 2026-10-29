"""Apex Spam X — font engine with markdown-safe transform + full patcher."""
import logging
import re

log = logging.getLogger("ApexSpam.fonts")

_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_LOWER = "abcdefghijklmnopqrstuvwxyz"
_DIGITS = "0123456789"


def _rmap(start, chars):
    return {c: chr(start + i) for i, c in enumerate(chars)}


_FONTS = {
    "normal": {},
    "bold": {**_rmap(0x1D400, _UPPER), **_rmap(0x1D41A, _LOWER), **_rmap(0x1D7CE, _DIGITS)},
    "italic": {
        **_rmap(0x1D434, _UPPER),
        **_rmap(0x1D44E, _LOWER[:7]),
        "h": "\u210E",
        **_rmap(0x1D456, _LOWER[8:]),
    },
    "script": {**_rmap(0x1D4D0, _UPPER), **_rmap(0x1D4EA, _LOWER)},
    "small": {
        "A": "ᴀ", "B": "ʙ", "C": "ᴄ", "D": "ᴅ", "E": "ᴇ", "F": "ꜰ", "G": "ɢ",
        "H": "ʜ", "I": "ɪ", "J": "ᴊ", "K": "ᴋ", "L": "ʟ", "M": "ᴍ", "N": "ɴ",
        "O": "ᴏ", "P": "ᴘ", "Q": "ǫ", "R": "ʀ", "S": "ꜱ", "T": "ᴛ", "U": "ᴜ",
        "V": "ᴠ", "W": "ᴡ", "X": "x", "Y": "ʏ", "Z": "ᴢ",
        "a": "ᴀ", "b": "ʙ", "c": "ᴄ", "d": "ᴅ", "e": "ᴇ", "f": "ꜰ", "g": "ɢ",
        "h": "ʜ", "i": "ɪ", "j": "ᴊ", "k": "ᴋ", "l": "ʟ", "m": "ᴍ", "n": "ɴ",
        "o": "ᴏ", "p": "ᴘ", "q": "ǫ", "r": "ʀ", "s": "ꜱ", "t": "ᴛ", "u": "ᴜ",
        "v": "ᴠ", "w": "ᴡ", "x": "x", "y": "ʏ", "z": "ᴢ",
    },
    "mono": {**_rmap(0x1D670, _UPPER), **_rmap(0x1D68A, _LOWER), **_rmap(0x1D7F6, _DIGITS)},
}

FONT_ORDER = ["normal", "bold", "italic", "script", "small", "mono"]
FONT_INDEX = {i: n for i, n in enumerate(FONT_ORDER)}
FONT_LABELS = {
    "normal": "Normal", "bold": "𝐁𝐨𝐥𝐝", "italic": "𝘐𝘵𝘢𝘭𝘪𝘤",
    "script": "𝓢𝓬𝓻𝓲𝓹𝓽", "small": "ꜱᴍᴀʟʟ", "mono": "𝙼𝚘𝚗𝚘",
}

ACTIVE_FONT = "normal"

# ── PROTECTED REGIONS (never transform) ──
_PROTECT = re.compile(
    r"<code>[\s\S]*?</code>"
    r"|<a\s[^>]*>[\s\S]*?</a>"
    r"|```[\s\S]*?```"
    r"|`[^`]*`"
    r"|\[[^\]\n]*\]\([^)\n]+\)"
    r"|https?://\S+"
    r"|tg://\S+"
    r"|<[^>]+>"
    r"|&[#a-zA-Z0-9]+;"
    r"|@[A-Za-z0-9_]{3,}"
)


def _trans(seg, table):
    return "".join(table.get(c, c) for c in seg)


def transform(text):
    """Unicode-transform plain text only; safe for HTML + markdown."""
    if not text or ACTIVE_FONT == "normal":
        return text
    table = _FONTS.get(ACTIVE_FONT)
    if not table:
        return text
    out, last = [], 0
    for m in _PROTECT.finditer(text):
        out.append(_trans(text[last:m.start()], table))
        out.append(m.group())
        last = m.end()
    out.append(_trans(text[last:], table))
    return "".join(out)


def fx(text):
    return transform(text)


# ── GLOBAL PATCHER (both client + Message) ──
_patched = False
_orig = {}


def _tx(message, kw):
    if isinstance(message, str):
        message = transform(message)
    if isinstance(kw.get("caption"), str):
        kw["caption"] = transform(kw["caption"])
    return message, kw


async def _p_send_message(self, entity, message=None, **kw):
    message, kw = _tx(message, kw)
    return await _orig["send_message"](self, entity, message, **kw)


async def _p_send_file(self, entity, file=None, **kw):
    _, kw = _tx(None, kw)
    return await _orig["send_file"](self, entity, file, **kw)


async def _p_edit_message(self, entity, message_id, text=None, **kw):
    if isinstance(text, str):
        text = transform(text)
    if isinstance(kw.get("caption"), str):
        kw["caption"] = transform(kw["caption"])
    return await _orig["edit_message"](self, entity, message_id, text, **kw)


async def _p_msg_reply(self, message=None, **kw):
    message, kw = _tx(message, kw)
    return await _orig["msg_reply"](self, message, **kw)


async def _p_msg_respond(self, message=None, **kw):
    message, kw = _tx(message, kw)
    return await _orig["msg_respond"](self, message, **kw)


async def _p_msg_edit(self, text=None, **kw):
    if isinstance(text, str):
        text = transform(text)
    if isinstance(kw.get("caption"), str):
        kw["caption"] = transform(kw["caption"])
    return await _orig["msg_edit"](self, text, **kw)


def patch():
    global _patched
    if _patched:
        return True
    try:
        from telethon import TelegramClient
        from telethon.tl.custom.message import Message

        _orig["send_message"] = TelegramClient.send_message
        _orig["send_file"] = TelegramClient.send_file
        _orig["edit_message"] = TelegramClient.edit_message
        _orig["msg_reply"] = Message.reply
        _orig["msg_respond"] = Message.respond
        _orig["msg_edit"] = Message.edit

        TelegramClient.send_message = _p_send_message
        TelegramClient.send_file = _p_send_file
        TelegramClient.edit_message = _p_edit_message
        Message.reply = _p_msg_reply
        Message.respond = _p_msg_respond
        Message.edit = _p_msg_edit
        _patched = True
        log.info("✅ Font patcher installed (client + Message)")
        return True
    except Exception as e:
        log.exception(f"❌ Font patch failed: {e}")
        return False


async def send_raw(client, *a, **kw):
    return await _orig["send_message"](client, *a, **kw)


async def edit_raw(client, *a, **kw):
    return await _orig["edit_message"](client, *a, **kw)


async def set_font(name):
    global ACTIVE_FONT
    if name not in _FONTS:
        return False
    ACTIVE_FONT = name
    try:
        from models.bot_settings import set_value
        await set_value("active_font", name)
    except Exception as e:
        log.warning(f"font persist: {e}")
    return True


async def sync_from_db():
    global ACTIVE_FONT
    try:
        from models.bot_settings import get_value
        name = await get_value("active_font")
        if name and name in _FONTS and name != ACTIVE_FONT:
            ACTIVE_FONT = name
            log.info(f"Font synced: {name}")
    except Exception as e:
        log.warning(f"font sync: {e}")
