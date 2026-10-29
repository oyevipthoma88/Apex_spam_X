from telethon import events, Button
from ApexSpam import HNDLR, OWNER_ID, CLIENTS
from ApexSpam import fonts
from ApexSpam.ui import header, quote, kv, divider


SAMPLE = "Apex Spam X 123"


def _preview(name):
    table = fonts._FONTS.get(name, {})
    if not table:
        return SAMPLE
    return "".join(table.get(c, c) for c in SAMPLE)


def _menu_text():
    active = fonts.FONT_LABELS.get(fonts.ACTIVE_FONT, fonts.ACTIVE_FONT)
    previews = []
    for name in fonts.FONT_ORDER:
        previews.append(f"<b>{fonts.FONT_LABELS[name]}</b>  →  <code>{_preview(name)}</code>")
    return (
        f"{header('font studio', '🎨')}\n\n"
        + quote(f"<b>Active</b>  :  <code>{active}</code>")
        + "\n\n"
        + quote("\n".join(previews), expandable=True)
        + f"\n\n{divider()}\n<i>Tap a font — applies instantly to all bots.</i>"
    )


def _menu_buttons():
    buttons = []
    row = []
    for name in fonts.FONT_ORDER:
        label = fonts.FONT_LABELS[name]
        if name == fonts.ACTIVE_FONT:
            label = f"✅ {label}"
        if len(row) == 2:
            buttons.append(row)
            row = []
        row.append(Button.inline(label, data=f"font_{name}".encode()))
    if row:
        buttons.append(row)
    buttons.append([Button.inline("« Back", data="start_back")])
    return buttons


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=rf"\{HNDLR}font(?: |$)(.*)"))
        async def font_cmd(event):
            if event.sender_id != OWNER_ID:
                return
            arg = (event.pattern_match.group(1) or "").strip().lower()
            if arg:
                name = fonts.FONT_INDEX.get(int(arg)) if arg.isdigit() else arg
                if name and await fonts.set_font(name):
                    return await event.reply(
                        f"{header('font applied', '🎨')}\n\n"
                        + quote(f"<b>Active</b>  :  <code>{fonts.FONT_LABELS[name]}</code>"),
                        parse_mode="html",
                    )
                return await event.reply(
                    f"{header('invalid font', '❌')}\n\n"
                    + quote(f"Available: <code>{', '.join(fonts.FONT_ORDER)}</code>\n"
                            f"Or index: <code>0-{len(fonts.FONT_ORDER)-1}</code>"),
                    parse_mode="html",
                )
            await fonts.send_raw(
                event.client, event.chat_id,
                _menu_text(), buttons=_menu_buttons(), parse_mode="html",
            )

        @c.on(events.CallbackQuery(pattern=rb"font_(\w+)"))
        async def font_cb(event):
            if event.sender_id != OWNER_ID:
                return await event.answer("Owner only.", alert=True)
            name = event.pattern_match.group(1).decode()
            ok = await fonts.set_font(name)
            if not ok:
                return await event.answer("Invalid font.", alert=True)
            await event.answer(f"Font → {fonts.FONT_LABELS[name]}")
            await fonts.edit_raw(
                event.client, event.chat_id, event.message_id,
                _menu_text(), buttons=_menu_buttons(), parse_mode="html",
            )


async def _open_menu(callback_event):
    """Called from help.py to open the font menu as a callback page."""
    if callback_event.sender_id != OWNER_ID:
        return await callback_event.answer("Owner only.", alert=True)
    await fonts.edit_raw(
        callback_event.client, callback_event.chat_id, callback_event.message_id,
        _menu_text(), buttons=_menu_buttons(), parse_mode="html",
    )
