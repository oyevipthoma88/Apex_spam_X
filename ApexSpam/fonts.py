"""Apex Spam X — font engine (Unicode transforms + global patcher)."""
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
    "bold": {
        **_rmap(0x1D400, _UPPER),
        **_rmap(0x1D41A, _LOWER),
        **_rmap(0x1D7CE, _DIGITS),
    },
    "italic": {
        **_rmap(0x1D434, _UPPER),
        **_rmap(0x1D44E, _LOWER[:7]),
        "h": "\u210E",
        **_rmap(0x1D456, _LOWER[8:]),
    },
    "script": {
        **_rmap(0x1D4D0, _UPPER),
        **_rmap(0x1D4EA, _LOWER),
    },
    "small": {
        "A": "ᴀ", "B": "ʙ", "C": "ᴄ", "D": "ᴅ", "E": "ᴇ", "F": "ꜰ",
        "G": "ɢ", "H": "ʜ", "I": "ɪ", "J": "ᴊ", "K": "ᴋ", "L": "ʟ",
        "M": "ᴍ", "N": "ɴ", "O": "ᴏ", "P": "ᴘ", "Q": "ǫ", "R": "ʀ",
        "S": "ꜱ", "T": "ᴛ", "U": "ᴜ", "V": "ᴠ", "W": "ᴡ", "X": "x",
        "Y": "ʏ", "Z": "ᴢ",
        "a": "ᴀ", "b": "ʙ", "c": "ᴄ", "d": "ᴅ", "e": "ᴇ", "f": "ꜰ",
        "g": "ɢ", "h": "ʜ", "i": "ɪ", "j": "ᴊ", "k": "ᴋ", "l": "ʟ",
        "m": "ᴍ", "n": "ɴ", "o": "ᴏ", "p": "ᴘ", "q": "ǫ", "r": "ʀ",
        "s": "ꜱ", "t": "ᴛ", "u": "ᴜ", "v": "ᴠ", "w": "ᴡ", "x": "x",
        "y": "ʏ", "z": "ᴢ",
    },
    "mono": {
        **_rmap(0x1D670, _UPPER),
        **_rmap(0x1D68A, _LOWER),
        **_rmap(0x1D7F6, _DIGITS),
    },
}

FONT_ORDER = ["normal", "bold", "italic", "script", "small", "mono"]
FONT_INDEX = {i: n for i, n in enumerate(FONT_ORDER)}
FONT_LABELS = {
    "normal": "Normal",
    "bold": "𝐁𝐨𝐥𝐝",
    "italic": "𝘐𝘵𝘢𝘭𝘪𝘤",
    "script": "𝓢𝓬𝓻𝓲𝓹𝓽",
    "small": "ꜱᴍᴀʟʟ",
    "mono": "𝙼𝚘𝚗𝚘",
}

ACTIVE_FONT = "normal"

_TAG_OR_ENTITY = re.compile(r"<[^>]+>|&[^;]+;")


def _trans(seg, table):
    return "".join(table.get(c, c) for c in seg)


def transform(text):
    if not text or ACTIVE_FONT == "normal":
        return text
    table = _FONTS.get(ACTIVE_FONT)
    if not table:
        return text
    out = []
    last = 0
    for m in _TAG_OR_ENTITY.finditer(text):
        out.append(_trans(text[last:m.start()], table))
        out.append(m.group())
        last = m.end()
    out.append(_trans(text[last:], table))
    return "".join(out)


_patched = False
_orig_send = None
_orig_file = None
_orig_edit = None


async def _p_send(self, entity, message=None, **kwargs):
    if isinstance(message, str):
        message = transform(message)
    if isinstance(kwargs.get("caption"), str):
        kwargs["caption"] = transform(kwargs["caption"])
    return await _orig_send(self, entity, message, **kwargs)


async def _p_file(self, entity, file=None, **kwargs):
    if isinstance(kwargs.get("caption"), str):
        kwargs["caption"] = transform(kwargs["caption"])
    return await _orig_file(self, entity, file, **kwargs)


async def _p_edit(self, entity, message_id, text=None, **kwargs):
    if isinstance(text, str):
        text = transform(text)
    if isinstance(kwargs.get("caption"), str):
        kwargs["caption"] = transform(kwargs["caption"])
    return await _orig_edit(self, entity, message_id, text, **kwargs)


def patch():
    global _patched, _orig_send, _orig_file, _orig_edit
    if _patched:
        return
    from telethon import TelegramClient
    _orig_send = TelegramClient.send_message
    _orig_file = TelegramClient.send_file
    _orig_edit = TelegramClient.edit_message
    TelegramClient.send_message = _p_send
    TelegramClient.send_file = _p_file
    TelegramClient.edit_message = _p_edit
    _patched = True
    log.info("✅ Font patcher installed")


async def send_raw(client, *args, **kwargs):
    return await _orig_send(client, *args, **kwargs)


async def edit_raw(client, *args, **kwargs):
    return await _orig_edit(client, *args, **kwargs)


async def set_font(name):
    global ACTIVE_FONT
    if name not in _FONTS:
        return False
    ACTIVE_FONT = name
    from models.bot_settings import set_value
    await set_value("active_font", name)
    return True


async def sync_from_db():
    global ACTIVE_FONT
    from models.bot_settings import get_value
    name = await get_value("active_font")
    if name and name in _FONTS and name != ACTIVE_FONT:
        ACTIVE_FONT = name
        log.info(f"Font synced: {name}")
