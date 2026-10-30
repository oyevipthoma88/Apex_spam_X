from telethon import events
from ApexSpam import HNDLR, OWNER_ID, CLIENTS
from ApexSpam import fonts, respond
from ApexSpam.ui import bread, quote, kv, pill, footer, join_rows
from ApexSpam.buttons import ib, copy_btn, grid

SAMPLE = "Apex Spam X 123"


def _preview(name):
    table = fonts._FONTS.get(name, {})
    return "".join(table.get(c, c) for c in SAMPLE) if table else SAMPLE


def _menu():
    active = fonts.FONT_LABELS.get(fonts.ACTIVE_FONT, fonts.ACTIVE_FONT)
    rows = [f"<b>{fonts.FONT_LABELS[n]}</b>  →  <code>{_preview(n)}</code>"
            for n in fonts.FONT_ORDER]
    text = (
        f"{bread('system', 'font')}\n\n"
        + quote(f"{pill(f'Active: {active}', 'ok')}\n{kv('Scope', 'all raid / spam data')}",
                expandable=True)
        + "\n\n"
        + quote("\n".join(rows), expandable=True)
        + f"\n{footer()}"
    )
    btns = []
    for n in fonts.FONT_ORDER:
        label = fonts.FONT_LABELS[n]
        kind = "success" if n == fonts.ACTIVE_FONT else "primary"
        if n == fonts.ACTIVE_FONT:
            label = "✅ " + label
        btns.append(ib(label, f"font:{n}".encode(), kind))
    rows_b = grid(btns, 2)
    cb = copy_btn("📋 Copy .font", f"{HNDLR}font {fonts.ACTIVE_FONT}")
    if cb:
        rows_b.append([cb])
    rows_b.append([ib("« Back", b"start_back", "primary")])
    return text, join_rows(rows_b)


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=rf"^[{HNDLR}!/]font(?: |$)(.*)"))
        async def font_cmd(e):
            if e.sender_id != OWNER_ID:
                return
            arg = (e.pattern_match.group(1) or "").strip().lower()
            if arg:
                name = fonts.FONT_INDEX.get(int(arg)) if arg.isdigit() else arg
                if name and await fonts.set_font(name):
                    return await e.reply(
                        f"{bread('system', 'font')}\n\n"
                        + quote(f"{pill('Applied', 'ok')}\n{kv('Font', fonts.FONT_LABELS[name])}"),
                        parse_mode="html",
                    )
                return await e.reply("❌ Invalid font.", parse_mode="html")
            text, btns = _menu()
            await e.reply(text, buttons=btns, parse_mode="html")

        @c.on(events.CallbackQuery(pattern=r"font:(\w+)"))
        async def font_cb(e):
            if e.sender_id != OWNER_ID:
                return await respond.ack(e, "Owner only", True)
            name = e.pattern_match.group(1)
            if isinstance(name, bytes):
                name = name.decode()
            if not await fonts.set_font(name):
                return await respond.ack(e, "Invalid font", True)
            await respond.ack(e, f"Font → {fonts.FONT_LABELS[name]}")
            text, btns = _menu()
            await respond.edit(e, text, btns)
