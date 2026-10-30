from telethon import events
from ApexSpam import HNDLR, OWNER_ID, CLIENTS
from ApexSpam import fonts
from ApexSpam.ui import header, quote, kv, divider
from ApexSpam.buttons import ib

SAMPLE = "Apex Spam X 123"


def _preview(name):
    table = fonts._FONTS.get(name, {})
    return "".join(table.get(c, c) for c in SAMPLE) if table else SAMPLE


def _menu_text():
    active = fonts.FONT_LABELS.get(fonts.ACTIVE_FONT, fonts.ACTIVE_FONT)
    rows = [f"<b>{fonts.FONT_LABELS[n]}</b>  →  <code>{_preview(n)}</code>" for n in fonts.FONT_ORDER]
    return (
        f"{header('font studio', '🎨')}\n\n"
        + quote(f"{kv('Active', active)}\n{kv('Scope', 'raids + spam + all replies')}")
        + "\n\n" + quote("\n".join(rows), expandable=True)
        + f"\n\n{divider()}\n<i>Tap a font — instant on all bots.</i>"
    )


def _menu_buttons():
    rows, row = [], []
    for n in fonts.FONT_ORDER:
        label = fonts.FONT_LABELS[n]
        kind = "success" if n == fonts.ACTIVE_FONT else "primary"
        if n == fonts.ACTIVE_FONT:
            label = f"✅ {label}"
        row.append(ib(label, f"font_{n}".encode(), kind))
        if len(row) == 2:
            rows.append(row); row = []
    if row: rows.append(row)
    rows.append([ib("« Back", b"start_back", "primary")])
    return rows


async def _open_menu(e):
    await fonts.send_raw(e.client, e.chat_id, _menu_text(), buttons=_menu_buttons(), parse_mode="html")


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=rf"^[\.!/]font(?: |$)(.*)"))
        async def font_cmd(e):
            if e.sender_id != OWNER_ID:
                return
            arg = (e.pattern_match.group(1) or "").strip().lower()
            if arg:
                name = fonts.FONT_INDEX.get(int(arg)) if arg.isdigit() else arg
                if name and await fonts.set_font(name):
                    return await e.reply(
                        f"{header('font applied', '🎨')}\n\n"
                        + quote(f"{kv('Active', fonts.FONT_LABELS[name])}\n{kv('Scope', 'all bots')}"),
                        parse_mode="html",
                    )
                return await e.reply(
                    f"{header('invalid font', '❌')}\n\n"
                    + quote(f"<code>{', '.join(fonts.FONT_ORDER)}</code>"),
                    parse_mode="html",
                )
            await _open_menu(e)

        @c.on(events.CallbackQuery(pattern=rb"font_(\w+)"))
        async def font_cb(e):
            if e.sender_id != OWNER_ID:
                return await e.answer("Owner only.", alert=True)
            name = e.pattern_match.group(1).decode()
            if not await fonts.set_font(name):
                return await e.answer("Invalid font.", alert=True)
            await e.answer(f"Font → {fonts.FONT_LABELS[name]}")
            await fonts.edit_raw(
                e.client, e.chat_id, e.message_id,
                _menu_text(), buttons=_menu_buttons(), parse_mode="html",
            )
