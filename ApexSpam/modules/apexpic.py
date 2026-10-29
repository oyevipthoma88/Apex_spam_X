from telethon import events
from ApexSpam import HNDLR, OWNER_ID, CLIENTS
from ApexSpam.ui import header, kv, quote
from models.bot_settings import set_value, get_value, del_value


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=rf"\{HNDLR}setpic(?: |$)"))
        async def setpic(e):
            if e.sender_id != OWNER_ID:
                return
            if not e.reply_to_msg_id:
                return await e.reply(
                    f"{header('setpic', '⚠️')}\n\n" + quote(f"Reply to a photo with <code>{HNDLR}setpic</code>"),
                    parse_mode="html",
                )
            r = await e.get_reply_message()
            if not r.photo and not (r.document and (r.document.mime_type or "").startswith("image/")):
                return await e.reply(f"{header('setpic', '❌')}\n\n" + quote("Not a photo."), parse_mode="html")
            data = await r.download_media(bytes)
            if not data or len(data) > 8 * 1024 * 1024:
                return await e.reply(f"{header('setpic', '❌')}\n\n" + quote("Too large / failed."), parse_mode="html")
            await set_value("start_pic", data)
            await e.reply(
                f"{header('start pic saved', '✅')}\n\n"
                + quote(f"{kv('Size', f'{len(data)//1024} KB')}\n{kv('Store', 'MongoDB')}", expandable=True),
                parse_mode="html",
            )

        @c.on(events.NewMessage(pattern=rf"\{HNDLR}delpic(?: |$)"))
        async def delpic(e):
            if e.sender_id != OWNER_ID:
                return
            ok = await del_value("start_pic")
            await e.reply(
                f"{header('start pic removed', '🗑️')}\n\n"
                + quote("Deleted from MongoDB." if ok else "No photo stored."),
                parse_mode="html",
            )

        @c.on(events.NewMessage(pattern=rf"\{HNDLR}setcaption(?: |$)"))
        async def setcaption(e):
            if e.sender_id != OWNER_ID:
                return
            parts = e.text.split(maxsplit=1)
            if len(parts) < 2:
                cur = await get_value("start_caption")
                return await e.reply(
                    f"{header('start caption', '📝')}\n\n"
                    + quote(
                        "Placeholders: <code>{header} {greet} {q1} {q2} {meta}</code>\n\n"
                        f"Current: {'custom' if cur else 'default'}",
                        expandable=True,
                    ),
                    parse_mode="html",
                )
            await set_value("start_caption", parts[1])
            await e.reply(f"{header('caption saved', '✅')}\n\n" + quote("Applies to all bots."), parse_mode="html")
