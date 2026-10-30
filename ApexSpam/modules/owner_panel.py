"""Apex Spam X — owner panel."""
from telethon import events

from ApexSpam import HNDLR, OWNER_ID, CLIENTS, HEROKU_APP_NAME, HEROKU_API_KEY
from ApexSpam.ui import header, quote, kv, footer
from ApexSpam.buttons import ib
from models.whitelist import add_gc, remove_gc, list_gcs


def _text():
    return (
        f"{header('owner panel', '👑')}\n\n"
        + quote(
            f"{kv('Clients', len(CLIENTS))}\n"
            f"{kv('Owner', OWNER_ID)}\n"
            f"{kv('Heroku', HEROKU_APP_NAME or 'not set')}",
            expandable=True,
        )
        + f"\n{footer()}"
    )


def _buttons():
    return [
        [ib("🔄 Update Bot", b"op_update", "primary")],
        [ib("📌 Add GC Whitelist", b"op_sudogc", "success")],
        [ib("📋 List Whitelisted", b"op_list", "primary")],
        [ib("✖ Close", b"op_close", "danger")],
    ]


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=rf"^[{HNDLR}!/]dev(?: |$)"))
        async def dev(e):
            if e.sender_id != OWNER_ID: return
            await e.reply(_text(), buttons=_buttons(), parse_mode="html")

        @c.on(events.CallbackQuery(data=b"op_update"))
        async def op_update(e):
            if e.sender_id != OWNER_ID:
                return await e.answer("Owner only", alert=True)
            if not HEROKU_APP_NAME or not HEROKU_API_KEY:
                return await e.answer("Heroku not configured", alert=True)
            try:
                import heroku3
                app = heroku3.from_key(HEROKU_API_KEY).app(HEROKU_APP_NAME)
                await e.answer("Restarting...")
                await e.edit(
                    f"{header('update', '🔄')}\n\n" + quote("Restarting via Heroku API…"),
                    parse_mode="html",
                )
                app.restart()
            except Exception as ex:
                await e.answer(str(ex)[:50], alert=True)

        @c.on(events.CallbackQuery(data=b"op_sudogc"))
        async def op_sudogc(e):
            if e.sender_id != OWNER_ID:
                return await e.answer("Owner only", alert=True)
            if e.is_private:
                return await e.answer("Run inside a group.", alert=True)
            await add_gc(e.chat_id)
            gcs = await list_gcs()
            await e.answer("Whitelisted")
            await e.edit(
                f"{header('sudogc', '📌')}\n\n"
                + quote(f"{kv('Chat', e.chat_id)}\n{kv('Total', len(gcs))}"),
                buttons=[[ib("« Back", b"op_back", "primary")]],
                parse_mode="html",
            )

        @c.on(events.CallbackQuery(data=b"op_list"))
        async def op_list(e):
            if e.sender_id != OWNER_ID:
                return await e.answer("Owner only", alert=True)
            gcs = await list_gcs()
            body = "\n".join(f"◈ <code>{g}</code>" for g in gcs[:20]) or "<i>none</i>"
            await e.edit(
                f"{header('whitelist', '📋')}\n\n" + quote(body, expandable=True),
                buttons=[[ib("« Back", b"op_back", "primary")]],
                parse_mode="html",
            )

        @c.on(events.CallbackQuery(data=b"op_close"))
        async def op_close(e):
            try: await e.delete()
            except Exception: pass

        @c.on(events.CallbackQuery(data=b"op_back"))
        async def op_back(e):
            await e.edit(_text(), buttons=_buttons(), parse_mode="html")

        @c.on(events.NewMessage(pattern=rf"^[{HNDLR}!/]sudogc(?: |$)"))
        async def sudogc(e):
            if e.sender_id != OWNER_ID: return
            if e.is_private:
                gcs = await list_gcs()
                body = "\n".join(f"◈ <code>{g}</code>" for g in gcs[:30]) or "<i>none</i>"
                return await e.reply(
                    f"{header('sudogc list', '📌')}\n\n" + quote(body, expandable=True),
                    parse_mode="html",
                )
            await add_gc(e.chat_id)
            gcs = await list_gcs()
            await e.reply(
                f"{header('sudogc', '📌')}\n\n"
                + quote(f"{kv('Chat', e.chat_id)}\n{kv('Total', len(gcs))}"),
                parse_mode="html",
            )

        @c.on(events.NewMessage(pattern=rf"^[{HNDLR}!/]unsudogc(?: |$)"))
        async def unsudogc(e):
            if e.sender_id != OWNER_ID: return
            if e.is_private: return
            ok = await remove_gc(e.chat_id)
            await e.reply(
                f"{header('unsudogc', '🗑️')}\n\n"
                + quote(f"{kv('Chat', e.chat_id)}\n{kv('Status', 'Removed' if ok else 'Not in list')}"),
                parse_mode="html",
            )
