"""Apex Spam X — owner panel: name/bio/pic + admin/sudo + heroku."""
import logging
import time

from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest

from ApexSpam import HNDLR, OWNER_ID, CLIENTS, HEROKU_APP_NAME, HEROKU_API_KEY
from ApexSpam.ui import header, quote, kv, footer, divider
from ApexSpam.buttons import ib
from models.whitelist import add_gc, remove_gc, list_gcs
from models.sudo import add_sudo, remove_sudo, mongo_ids
from models.admins import add_admin, remove_admin, list_admins

log = logging.getLogger("ApexSpam.owner_panel")
PENDING = {}


def _text():
    return (
        f"{header('owner panel', '👑')}\n\n"
        + quote(
            f"{kv('Clients', len(CLIENTS))}\n"
            f"{kv('Owner', OWNER_ID)}\n"
            f"{kv('Heroku', HEROKU_APP_NAME or 'not set')}",
            expandable=True,
        )
        + f"\n{divider()}\n{footer()}"
    )


def _buttons():
    return [
        [ib("✏️ Set Name", b"op_setname", "primary"),
         ib("📝 Set Bio", b"op_setbio", "primary")],
        [ib("🖼️ Set Photo", b"op_setpic", "primary")],
        [ib("👤 Add Admin", b"op_addadmin", "success"),
         ib("🚫 Remove Admin", b"op_deladmin", "danger")],
        [ib("🛡️ Add Sudo", b"op_addsudo", "success"),
         ib("⚔️ Remove Sudo", b"op_delsudo", "danger")],
        [ib("📌 Add GC", b"op_sudogc", "success"),
         ib("📋 List", b"op_list", "primary")],
        [ib("🔄 Update Bot", b"op_update", "primary"),
         ib("✖ Close", b"op_close", "danger")],
    ]


async def _apply_name(new_name: str):
    ok = 0
    for c in CLIENTS:
        try:
            await c(UpdateProfileRequest(first_name=new_name))
            ok += 1
        except Exception as ex:
            log.warning(f"name fail {id(c)}: {ex}")
    return ok


async def _apply_bio(new_bio: str):
    ok = 0
    for c in CLIENTS:
        try:
            await c(UpdateProfileRequest(about=new_bio))
            ok += 1
        except Exception as ex:
            log.warning(f"bio fail: {ex}")
    return ok


async def _apply_pic(file_bytes):
    ok = 0
    for c in CLIENTS:
        try:
            uploaded = await c.upload_file(file_bytes)
            await c(UploadProfilePhotoRequest(file=uploaded))
            ok += 1
        except Exception as ex:
            log.warning(f"pic fail: {ex}")
    return ok


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=rf"^[{HNDLR}!/]dev(?: |$)"))
        async def dev(e):
            if e.sender_id != OWNER_ID: return
            await e.reply(_text(), buttons=_buttons(), parse_mode="html")

        @c.on(events.NewMessage(pattern=rf"^[{HNDLR}!/]setname(?: |$)"))
        async def setname(e):
            if e.sender_id != OWNER_ID: return
            parts = e.text.split(maxsplit=1)
            if len(parts) < 2:
                return await e.reply(f"<code>{HNDLR}setname New Name</code>",
                                     parse_mode="html")
            n = parts[1][:64]
            ok = await _apply_name(n)
            await e.reply(
                f"{header('set name', '✏️')}\n\n"
                + quote(f"{kv('Name', n)}\n{kv('Updated', f'{ok}/{len(CLIENTS)}')}",
                        expandable=True),
                parse_mode="html",
            )

        @c.on(events.NewMessage(pattern=rf"^[{HNDLR}!/]setbio(?: |$)"))
        async def setbio(e):
            if e.sender_id != OWNER_ID: return
            parts = e.text.split(maxsplit=1)
            if len(parts) < 2:
                return await e.reply(f"<code>{HNDLR}setbio New bio</code>",
                                     parse_mode="html")
            b = parts[1][:140]
            ok = await _apply_bio(b)
            await e.reply(
                f"{header('set bio', '📝')}\n\n"
                + quote(f"{kv('Bio', b[:40])}\n{kv('Updated', f'{ok}/{len(CLIENTS)}')}",
                        expandable=True),
                parse_mode="html",
            )

        @c.on(events.NewMessage(pattern=rf"^[{HNDLR}!/]setbotpic(?: |$)"))
        async def setbotpic(e):
            if e.sender_id != OWNER_ID: return
            if not e.reply_to_msg_id:
                return await e.reply("Reply to a photo.", parse_mode="html")
            r = await e.get_reply_message()
            if not r.photo and not (r.document and "image" in (r.document.mime_type or "")):
                return await e.reply("❌ Not a photo.", parse_mode="html")
            data = await r.download_media(file=bytes)
            if not data:
                return await e.reply("❌ Download failed.", parse_mode="html")
            ok = await _apply_pic(data)
            await e.reply(
                f"{header('set photo', '🖼️')}\n\n"
                + quote(f"{kv('Updated', f'{ok}/{len(CLIENTS)}')}"),
                parse_mode="html",
            )

        @c.on(events.CallbackQuery(data=b"op_setname"))
        async def cb_setname(e):
            if e.sender_id != OWNER_ID: return await e.answer("Owner only", alert=True)
            await e.answer("Send: .setname New Name", alert=True)

        @c.on(events.CallbackQuery(data=b"op_setbio"))
        async def cb_setbio(e):
            if e.sender_id != OWNER_ID: return await e.answer("Owner only", alert=True)
            await e.answer("Send: .setbio New bio", alert=True)

        @c.on(events.CallbackQuery(data=b"op_setpic"))
        async def cb_setpic(e):
            if e.sender_id != OWNER_ID: return await e.answer("Owner only", alert=True)
            await e.answer("Reply photo: .setbotpic", alert=True)

        @c.on(events.CallbackQuery(data=b"op_update"))
        async def op_update(e):
            if e.sender_id != OWNER_ID: return await e.answer("Owner only", alert=True)
            if not HEROKU_APP_NAME or not HEROKU_API_KEY:
                return await e.answer("Heroku not configured", alert=True)
            try:
                import heroku3
                app = heroku3.from_key(HEROKU_API_KEY).app(HEROKU_APP_NAME)
                await e.answer("Restarting...")
                app.restart()
            except Exception as ex:
                await e.answer(str(ex)[:50], alert=True)

        @c.on(events.CallbackQuery(data=b"op_sudogc"))
        async def op_sudogc(e):
            if e.sender_id != OWNER_ID: return await e.answer("Owner only", alert=True)
            if e.is_private: return await e.answer("Group me chalao", alert=True)
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
            if e.sender_id != OWNER_ID: return await e.answer("Owner only", alert=True)
            gcs = await list_gcs()
            admins = await list_admins()
            sudos = await mongo_ids()
            body = (
                f"<b>📌 GCs ({len(gcs)})</b>\n"
                + ("\n".join(f"◈ <code>{g}</code>" for g in gcs[:10]) or "<i>none</i>")
                + f"\n\n<b>👤 Admins ({len(admins)})</b>\n"
                + ("\n".join(f"◈ <code>{a}</code>" for a in admins[:10]) or "<i>none</i>")
                + f"\n\n<b>🛡️ Sudos ({len(sudos)})</b>\n"
                + ("\n".join(f"◈ <code>{s}</code>" for s in sudos[:10]) or "<i>none</i>")
            )
            await e.edit(
                f"{header('lists', '📋')}\n\n" + quote(body, expandable=True),
                buttons=[[ib("« Back", b"op_back", "primary")]],
                parse_mode="html",
            )

        @c.on(events.CallbackQuery(data=b"op_addadmin"))
        async def op_addadmin(e):
            if e.sender_id != OWNER_ID: return await e.answer("Owner only", alert=True)
            await e.answer("Send: .addadmin <id|@user|reply>", alert=True)

        @c.on(events.CallbackQuery(data=b"op_deladmin"))
        async def op_deladmin(e):
            if e.sender_id != OWNER_ID: return await e.answer("Owner only", alert=True)
            await e.answer("Send: .deladmin <id>", alert=True)

        @c.on(events.CallbackQuery(data=b"op_addsudo"))
        async def op_addsudo(e):
            if e.sender_id != OWNER_ID: return await e.answer("Owner only", alert=True)
            await e.answer("Send: .addsudo <id>", alert=True)

        @c.on(events.CallbackQuery(data=b"op_delsudo"))
        async def op_delsudo(e):
            if e.sender_id != OWNER_ID: return await e.answer("Owner only", alert=True)
            await e.answer("Send: .delsudo <id>", alert=True)

        @c.on(events.CallbackQuery(data=b"op_close"))
        async def op_close(e):
            try: await e.delete()
            except Exception: pass

        @c.on(events.CallbackQuery(data=b"op_back"))
        async def op_back(e):
            await e.edit(_text(), buttons=_buttons(), parse_mode="html")

        # Admin management
        @c.on(events.NewMessage(pattern=rf"^[{HNDLR}!/]addadmin(?: |$)"))
        async def addadmin(e):
            if e.sender_id != OWNER_ID: return
            uid = await _resolve(e)
            if not uid: return await e.reply("❌ user id/reply/@user do", parse_mode="html")
            await add_admin(uid)
            await e.reply(f"✅ Admin added: <code>{uid}</code>", parse_mode="html")

        @c.on(events.NewMessage(pattern=rf"^[{HNDLR}!/]deladmin(?: |$)"))
        async def deladmin(e):
            if e.sender_id != OWNER_ID: return
            uid = await _resolve(e)
            if not uid: return
            ok = await remove_admin(uid)
            await e.reply(f"🗑️ {'Removed' if ok else 'Not in list'}: <code>{uid}</code>",
                          parse_mode="html")

        @c.on(events.NewMessage(pattern=rf"^[{HNDLR}!/]listadmin(?: |$)"))
        async def listadmin(e):
            if e.sender_id != OWNER_ID: return
            admins = await list_admins()
            body = "\n".join(f"◈ <code>{a}</code>" for a in admins) or "<i>none</i>"
            await e.reply(f"{header('admins', '👤')}\n\n" + quote(body, expandable=True),
                          parse_mode="html")


async def _resolve(e):
    parts = e.text.split(maxsplit=1)
    arg = parts[1].strip() if len(parts) > 1 else ""
    if arg and arg.lstrip("-").isdigit():
        return int(arg)
    if e.reply_to_msg_id:
        r = await e.get_reply_message()
        return r.sender_id
    if arg:
        try:
            ent = await e.client.get_entity(arg)
            return ent.id
        except Exception:
            return None
    return None
