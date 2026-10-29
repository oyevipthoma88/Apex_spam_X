"""Apex Spam X — premium HTML card builders."""
import html

TOP = "╭━━━━━━━━━━━━━━━━━━━━╮"
BOT = "╰━━━━━━━━━━━━━━━━━━━━╯"


def esc(s) -> str:
    return html.escape(str(s), quote=False)


def header(title: str, emoji: str = "⚡") -> str:
    spaced = " ".join(title.upper())
    return f"<b>{TOP}</b>\n   {emoji} <b>{esc(spaced)}</b> {emoji}\n<b>{BOT}</b>"


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
