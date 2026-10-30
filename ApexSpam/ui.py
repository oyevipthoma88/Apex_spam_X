"""Apex Spam X — premium HTML cards (fixed tags)."""
import html
import re

BRAND = "Apex Spam X"
TOP = "╭━━━━━━━━━━━━━━━━━━━━╮"
BOT = "╰━━━━━━━━━━━━━━━━━━━━╯"
_TOKEN = re.compile(r"\{(header|greet|q1|q2|meta)\}")


def esc(s):
    return html.escape(str(s), quote=False)


def safe_format(tpl, **vals):
    if not isinstance(tpl, str):
        return ""
    return _TOKEN.sub(lambda m: str(vals.get(m.group(1), "")), tpl)


def header(title, emoji="⚡"):
    spaced = " ".join(str(title).upper())
    return f"<b>{TOP}</b>\n   {emoji} <b>{esc(spaced)}</b> {emoji}\n<b>{BOT}</b>"


def title(text, emoji="⚡"):
    return f"{emoji} <b>{esc(str(text).upper())}</b>"


def quote(text, expandable=False):
    tag = "blockquote expandable" if expandable else "blockquote"
    return f"<{tag}>{text}</{tag}>"


def kv(key, value):
    return f"◈ <b>{esc(key)}</b>  :  <code>{esc(value)}</code>"


def section(name):
    return f"╭─〔 <b>{esc(name)}</b> 〕─╮"


def divider():
    return "┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄"


def link_user(uid, name):
    return f'<a href="tg://user?id={int(uid)}">{esc(name)}</a>'


def bar(value, limit=1000, size=10):
    ratio = max(0.0, min(1.0, 1 - (value / limit)))
    filled = int(round(ratio * size))
    return "▰" * filled + "▱" * (size - filled)


def footer(text=BRAND):
    return f"<i>{esc(text)}</i>"


def bread(*parts, emoji="⚡"):
    trail = " › ".join(esc(str(p).upper()) for p in parts)
    return f"{emoji} <b>{esc(BRAND.upper())}</b>  ·  {trail}"


def pill(label, state="ok"):
    icon = {"ok": "🟢", "warn": "🟡", "bad": "🔴", "info": "🔵"}.get(state, "⚪")
    return f"{icon} <b>{esc(label)}</b>"


def prog(cur, total, width=10):
    total = max(1, int(total))
    cur = min(max(0, int(cur)), total)
    filled = int(round(cur / total * width))
    pct = int(round(cur / total * 100))
    bar_ = "▰" * filled + "▱" * (width - filled)
    return f"<code>{bar_}</code>  <b>{pct}%</b>  <code>{cur}/{total}</code>"


def spoil(text):
    return f"<tg-spoiler>{esc(text)}</tg-spoiler>"


def table(headers, rows):
    headers = [str(h) for h in headers]
    rows = [[str(c) for c in r] for r in rows]
    cols = len(headers)
    widths = [len(h) for h in headers]
    for r in rows:
        for i in range(min(cols, len(r))):
            widths[i] = max(widths[i], len(r[i]))

    def line(r):
        return "  ".join(r[i].ljust(widths[i]) for i in range(cols))

    out = [line(headers), "─" * (sum(widths) + 2 * (cols - 1))]
    out += [line(r) for r in rows]
    return "<pre>" + esc("\n".join(out)) + "</pre>"


def card(title_, body, emoji="⚡", footer_text=None):
    out = f"{header(title_, emoji)}\n\n{quote(body, expandable=True)}"
    if footer_text:
        out += f"\n{footer(footer_text)}"
    return out


def join_rows(rows):
    return [[b for b in row if b] for row in rows if any(row)]
