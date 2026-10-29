"""Apex Spam X — premium HTML card builders."""
import html

BRAND = "Apex Spam X"
TOP = "╭━━━━━━━━━━━━━━━━━━━━╮"
BOT = "╰━━━━━━━━━━━━━━━━━━━━╯"


def esc(s):
    return html.escape(str(s), quote=False)


def header(title, emoji="⚡"):
    spaced = " ".join(title.upper())
    return f"<b>{TOP}</b>\n   {emoji} <b>{esc(spaced)}</b> {emoji}\n<b>{BOT}</b>"


def quote(text, expandable=False):
    tag = "blockquote expandable" if expandable else "blockquote"
    return f"<{tag}>{text}</{tag}>"


def kv(key, value):
    return f"◈ <b>{esc(key)}</b>  :  <code>{esc(value)}</code>"


def divider():
    return "┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄"


def link_user(uid, name):
    return f'<a href="tg://user?id={uid}">{esc(name)}</a>'


def bar(value, limit=1000, size=10):
    ratio = max(0.0, min(1.0, 1 - (value / limit)))
    filled = int(round(ratio * size))
    return "▰" * filled + "▱" * (size - filled)


def footer(text="powered by Apex Spam X"):
    return f"<i>{esc(text)}</i>"
