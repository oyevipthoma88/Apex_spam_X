"""Apex Spam X — premium HTML card builders."""
import html
import re

BRAND = "Apex Spam X"
TOP = "╭━━━━━━━━━━━━━━━━━━━━╮"
BOT = "╰━━━━━━━━━━━━━━━━━━━━╯"

_TOKEN = re.compile(r"\{(header|greet|q1|q2|meta)\}")


def esc(s) -> str:
    return html.escape(str(s), quote=False)


def safe_format(tpl, **vals) -> str:
    if not isinstance(tpl, str):
        return ""
    return _TOKEN.sub(lambda m: str(vals.get(m.group(1), "")), tpl)


def header(title: str, emoji: str = "⚡") -> str:
    spaced = " ".join(title.upper())
    return f"<b>{TOP}</b>\n   {emoji} <b>{esc(spaced)}</b> {emoji}\n<b>{BOT}</b>"


def title(text: str, emoji: str = "⚡") -> str:
    return f"{emoji} <b>{esc(text.upper())}</b>"


def quote(text: str, expandable: bool = False) -> str:
    tag = "blockquote expandable" if expandable else "blockquote"
    return f"<{tag}>{text}</{tag}>"


def kv(key: str, value) -> str:
    return f"◈ <b>{esc(key)}</b>  :  <code>{esc(value)}</code>"


def section(name: str) -> str:
    return f"╭─〔 <b>{esc(name)}</b> 〕─╮"


def divider() -> str:
    return "┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄"


def link_user(uid, name: str) -> str:
    return f'<a href="tg://user?id={uid}">{esc(name)}</a>'


def bar(value, limit=1000, size=10) -> str:
    ratio = max(0.0, min(1.0, 1 - (value / limit)))
    filled = int(round(ratio * size))
    return "▰" * filled + "▱" * (size - filled)


def footer(text="Apex Spam X") -> str:
    return f"<i>{esc(text)}</i>"
