"""Apex Spam X — owner panel: name/bio/photo for ALL bots."""
import logging

from telethon import events, TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.bots import SetBotInfoRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest

from ApexSpam import (
    HNDLR, OWNER_ID, CLIENTS, HEROKU_APP_NAME, HEROKU_API_KEY,
    USER_SESSION, API_ID, API_HASH,
)
from ApexSpam.ui import header, quote, kv, footer, divider
from ApexSpam.buttons import ib
from models.whitelist import add_gc, list_gcs
from models.sudo import mongo_ids
from models.admins import add_admin, remove_admin, list_admins

log = logging.getLogger("ApexSpam.owner_panel")

PENDING = {}      # chat_id -> (action, prompt_msg_id)
_user_client = None


async def _get_user_client():
    global _user_client
    if _user_client is not None:
        return _user_client
    if not USER_SESSION:
        return None
    try:
        uc = TelegramClient(StringSession(USER_SESSION), API_ID, API_HASH)
        await uc.connect()
        if not await uc.is_user_authorized():
            await uc.disconnect()
            return None
        _user_client = uc
        log.info("✅ user session connected (photo support)")
        return uc
    except Exception as e:
        log.warning(f"user client failed: {e}")
        return None


async def _apply_name(name: str):
    from ApexSpam.fonts import asciify
    clean = asciify(name)[:64]
    ok = 0
    for c in CLIENTS:
        uname = "?"
        try:
            me = await c.get_me()
            uname = me.username or "?"
            # Try with explicit bot param + lang_code en
            try:
                await c(SetBotInfoRequest(bot=me.id, lang_code="en", name=clean))
            except Exception:
                await c(SetBotInfoRequest(lang_code="", name=clean))
            ok += 1
            log.info(f"name set @{uname} -> {clean!r}")
        except Exception as ex:
            log.warning(f"name fail @{uname}: {ex}")
    return ok


async def _apply_bio(bio: str):
    from ApexSpam.fonts import asciify
    clean = asciify(bio)[:120]
    ok = 0
    for c in CLIENTS:
        uname = "?"
        try:
            me = await c.get_me()
            uname = me.username or "?"
            try:
                await c(SetBotInfoRequest(bot=me.id, lang_code="en", about=clean))
            except Exception:
                await c(SetBotInfoRequest(lang_code="", about=clean))
            try:
                await c(SetBotInfoRequest(bot=me.id, lang_code="en", description=clean))
            except Exception:
                pass
            ok += 1
            log.info(f"bio set @{uname} -> {clean[:30]!r}")
        except Exception as ex:
            log.warning(f"bio fail @{uname}: {ex}")
    return ok


async def _apply_pic(data: bytes):
    """Profile photo requires user session (bot cannot set own photo)."""
    uc = await _get_user_client()
    if uc is None:
        return -1  # signal "needs USER_SESSION"
    ok = 0
    for c in CLIENTS:
        try:
            me = await c.get_me()
            uploaded = await uc.upload_file(data)
            await uc(UploadProfilePhotoRequest(
                fallback=True, bot=me.username, file=uploaded,
            ))
            ok += 1
        except Exception as ex:
            log.warning(f"pic fail @{getattr(me,'username','?')}: {ex}")
    return ok


def _text():
    return (
        f"{header('owner panel', '👑')}\n\n"
        + quote(
            f"{kv('Clients', len(CLIENTS))}\n"
            f"{kv('Owner', OWNER_ID)}\n"
            f"{kv('User session', '✅ set' if USER_SESSION else '❌ missing')}\n"
            f"{kv('Heroku', HEROKU_APP_NAME or 'not set')}",
            expandable=True,
        )
        + f"\n{divider()}\n{footer()}"
    )


def _buttons():
    return [
        [ib("✏️ Set Name", b"op_setname", "primary"),
         ib("📝 Set Bio", b"op_setbio", "primary")],
        [ib("🖼️ Set Photo", b"op_setpic", "primary"),
         ib("🎨 Set Start Pic", b"op_setstartpic", "success")],
        [ib("👤 Add Admin", b"op_addadmin", "success"),
         ib("🚫 Remove Admin", b"op_deladmin", "danger")],
        [ib("🛡️ Add Sudo", b"op_addsudo", "success"),
         ib("⚔️ Remove Sudo", b"op_delsudo", "danger")],
        [ib("📌 Add GC", b"op_sudogc", "success"),
         ib("📋 List All", b"op_list", "primary")],
        [ib("🔄 Update Bot", b"op_update", "primary"),
         ib("✖ Close", b"op_close", "danger")],
    ]


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


def register():
    for c in CLIENTS:
        # ── panel ──
        @c.on(events.NewMessage(pattern=r"^[\.!/]dev(?: |$)"))
        async def dev(e):
            if e.sender_id != OWNER_ID: return
            await e.reply(_text(), buttons=_buttons(), parse_mode="html")

        # ── button prompts ──
        @c.on(events.CallbackQuery(data=b"op_setname"))
        async def cb_setname(e):
            if e.sender_id != OWNER_ID:
                return await e.answer("Owner only", alert=True)
            m = await e.edit(
                f"{header('set name', '✏️')}\n\n"
                + quote("Reply to this message with the <b>new name</b>.\n"
                        f"Or: <code>.setname New Name</code>"),
                parse_mode="html",
            )
            PENDING[e.chat_id] = ("setname", m.id)
            await e.answer("Reply with name")

        @c.on(events.CallbackQuery(data=b"op_setbio"))
        async def cb_setbio(e):
            if e.sender_id != OWNER_ID:
                return await e.answer("Owner only", alert=True)
            m = await e.edit(
                f"{header('set bio', '📝')}\n\n"
                + quote("Reply to this message with the <b>new bio</b>.\n"
                        f"Or: <code>.setbio Your bio</code>"),
                parse_mode="html",
            )
            PENDING[e.chat_id] = ("setbio", m.id)
            await e.answer("Reply with bio")

        @c.on(events.CallbackQuery(data=b"op_setstartpic"))
        async def cb_setstartpic(e):
            if e.sender_id != OWNER_ID:
                return await e.answer("Owner only", alert=True)
            m = await e.edit(
                f"{header('set start pic', '🎨')}\n\n"
                + quote(
                    "Reply to this message with a <b>photo</b>.\n"
                    "This photo will show on <code>/start</code> for everyone,\n"
                    "and stays saved forever (MongoDB)."
                ),
                parse_mode="html",
            )
            PENDING[e.chat_id] = ("setstartpic", m.id)
            await e.answer("Reply with photo")

        @c.on(events.CallbackQuery(data=b"op_setpic"))
        async def cb_setpic(e):
            if e.sender_id != OWNER_ID:
                return await e.answer("Owner only", alert=True)
            if not USER_SESSION:
                return await e.answer("USER_SESSION missing in Heroku", alert=True)
            m = await e.edit(
                f"{header('set photo', '🖼️')}\n\n"
                + quote("Reply to this message with a <b>photo</b>.\n"
                        f"Or reply to any photo: <code>.setbotpic</code>"),
                parse_mode="html",
            )
            PENDING[e.chat_id] = ("setpic", m.id)
            await e.answer("Reply with photo")

        # ── direct commands ──
        @c.on(events.NewMessage(pattern=r"^[\.!/]setname(?: |$)"))
        async def setname(e):
            if e.sender_id != OWNER_ID: return
            parts = e.text.split(maxsplit=1)
            if len(parts) < 2:
                return await e.reply("<code>.setname New Name</code>", parse_mode="html")
            name = parts[1][:64]
            ok = await _apply_name(name)
            await e.reply(
                f"{header('set name', '✏️')}\n\n"
                + quote(f"{kv('Name', name)}\n{kv('Updated', f'{ok}/{len(CLIENTS)}')}",
                        expandable=True),
                parse_mode="html",
            )

        @c.on(events.NewMessage(pattern=r"^[\.!/]setbio(?: |$)"))
        async def setbio(e):
            if e.sender_id != OWNER_ID: return
            parts = e.text.split(maxsplit=1)
            if len(parts) < 2:
                return await e.reply("<code>.setbio Your bio</code>", parse_mode="html")
            bio = parts[1][:140]
            ok = await _apply_bio(bio)
            await e.reply(
                f"{header('set bio', '📝')}\n\n"
                + quote(f"{kv('Bio', bio[:40])}\n{kv('Updated', f'{ok}/{len(CLIENTS)}')}",
                        expandable=True),
                parse_mode="html",
            )

        @c.on(events.NewMessage(pattern=r"^[\.!/]setbotpic(?: |$)"))
        async def setbotpic(e):
            if e.sender_id != OWNER_ID: return
            if not USER_SESSION:
                return await e.reply(
                    "❌ <code>USER_SESSION</code> Heroku me set karo (profile photo ke liye user session chahiye).",
                    parse_mode="html",
                )
            if not e.reply_to_msg_id:
                return await e.reply("Reply to a photo.", parse_mode="html")
            r = await e.get_reply_message()
            if not r.photo and not (r.document and "image" in (r.document.mime_type or "")):
                return await e.reply("❌ Not a photo.", parse_mode="html")
            data = await r.download_media(file=bytes)
            if not data:
                return await e.reply("❌ Download failed.", parse_mode="html")
            ok = await _apply_pic(data)
            if ok == -1:
                return await e.reply("❌ USER_SESSION missing.", parse_mode="html")
            await e.reply(
                f"{header('set photo', '🖼️')}\n\n"
                + quote(f"{kv('Updated', f'{ok}/{len(CLIENTS)}')}"),
                parse_mode="html",
            )

        # ── interactive reply ──
        @c.on(events.NewMessage())
        async def handle_pending(e):
            if e.sender_id != OWNER_ID: return
            if e.text and e.text.startswith((".", "!", "/", "?")): return
            entry = PENDING.get(e.chat_id)
            if not entry: return
            action, prompt_id = entry
            if e.reply_to_msg_id != prompt_id: return
            PENDING.pop(e.chat_id, None)

            if action == "setname" and e.text:
                ok = await _apply_name(e.text[:64])
                await e.reply(
                    f"{header('set name', '✏️')}\n\n"
                    + quote(f"{kv('Name', e.text[:64])}\n{kv('Updated', f'{ok}/{len(CLIENTS)}')}",
                            expandable=True),
                    parse_mode="html",
                )
            elif action == "setbio" and e.text:
                ok = await _apply_bio(e.text[:140])
                await e.reply(
                    f"{header('set bio', '📝')}\n\n"
                    + quote(f"{kv('Bio', e.text[:40])}\n{kv('Updated', f'{ok}/{len(CLIENTS)}')}",
                            expandable=True),
                    parse_mode="html",
                )
            elif action == "setstartpic":
                if not e.photo and not (
                    e.document and "image" in (e.document.mime_type or "")
                ):
                    return await e.reply("❌ Not a photo. Try again.", parse_mode="html")
                data = await e.download_media(file=bytes)
                if not data:
                    return await e.reply("❌ Download failed.", parse_mode="html")
                if len(data) > 8 * 1024 * 1024:
                    return await e.reply("❌ Too large (max 8 MB).", parse_mode="html")
                from ApexSpam.modules.apexpic import _detect_ext
                from models.bot_settings import set_value
                ext = _detect_ext(data)
                await set_value("start_pic", data)
                await set_value("start_pic_ext", ext)
                await e.reply(
                    f"{header('start pic saved', '✅')}\n\n"
                    + quote(
                        f"{kv('Size', f'{len(data)//1024} KB')}\n"
                        f"{kv('Format', ext)}\n"
                        f"{kv('Store', 'MongoDB — survives restart')}",
                        expandable=True,
                    ),
                    parse_mode="html",
                )

            elif action == "setpic":
                if not e.photo and not (e.document and "image" in (e.document.mime_type or "")):
                    return await e.reply("❌ Not a photo. Try again.", parse_mode="html")
                data = await e.download_media(file=bytes)
                if not data:
                    return await e.reply("❌ Download failed.", parse_mode="html")
                ok = await _apply_pic(data)
                await e.reply(
                    f"{header('set photo', '🖼️')}\n\n"
                    + quote(f"{kv('Updated', f'{ok}/{len(CLIENTS)}')}"),
                    parse_mode="html",
                )

        # ── heroku / gc / list ──
        @c.on(events.CallbackQuery(data=b"op_update"))
        async def op_update(e):
            if e.sender_id != OWNER_ID: return await e.answer("Owner only", alert=True)
            if not HEROKU_APP_NAME or not HEROKU_API_KEY:
                return await e.answer("Heroku not configured", alert=True)
            try:
                import heroku3
                app = heroku3.from_key(HEROKU_API_KEY).app(HEROKU_APP_NAME)
                await e.edit(
                    f"{header('update', '🔄')}\n\n" + quote("Restarting via Heroku API…"),
                    parse_mode="html",
                )
                app.restart()
            except Exception as ex:
                await e.answer(str(ex)[:50], alert=True)

        @c.on(events.CallbackQuery(data=b"op_sudogc"))
        async def op_sudogc(e):
            if e.sender_id != OWNER_ID: return await e.answer("Owner only", alert=True)
            if e.is_private: return await e.answer("Group me chalao", alert=True)
            await add_gc(e.chat_id)
            gcs = await list_gcs()
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

        for data, help_txt in [
            (b"op_addadmin", ".addadmin <id|@user|reply>"),
            (b"op_deladmin", ".deladmin <id|@user|reply>"),
            (b"op_addsudo", ".addsudo <id|@user|reply>"),
            (b"op_delsudo", ".delsudo <id|@user|reply>"),
        ]:
            def _mk(ht):
                async def cb(e):
                    if e.sender_id != OWNER_ID:
                        return await e.answer("Owner only", alert=True)
                    await e.edit(
                        f"{header('action', '👤')}\n\n"
                        + quote(f"Send: <code>{ht}</code>"),
                        buttons=[[ib("« Back", b"op_back", "primary")]],
                        parse_mode="html",
                    )
                return cb
            c.on(events.CallbackQuery(data=data))(_mk(help_txt))

        @c.on(events.CallbackQuery(data=b"op_close"))
        async def op_close(e):
            try: await e.delete()
            except Exception: pass

        @c.on(events.CallbackQuery(data=b"op_back"))
        async def op_back(e):
            await e.edit(_text(), buttons=_buttons(), parse_mode="html")

        # ── admin/sudo commands ──
        @c.on(events.NewMessage(pattern=r"^[\.!/]addadmin(?: |$)"))
        async def addadmin(e):
            if e.sender_id != OWNER_ID: return
            uid = await _resolve(e)
            if not uid:
                return await e.reply("❌ id / reply / @user do", parse_mode="html")
            await add_admin(uid)
            await e.reply(f"✅ Admin added: <code>{uid}</code>", parse_mode="html")

        @c.on(events.NewMessage(pattern=r"^[\.!/]deladmin(?: |$)"))
        async def deladmin(e):
            if e.sender_id != OWNER_ID: return
            uid = await _resolve(e)
            if not uid: return
            ok = await remove_admin(uid)
            await e.reply(f"{'🗑️ Removed' if ok else '❌ Not in list'}: <code>{uid}</code>",
                          parse_mode="html")

        @c.on(events.NewMessage(pattern=r"^[\.!/]listadmin(?: |$)"))
        async def listadmin(e):
            if e.sender_id != OWNER_ID: return
            admins = await list_admins()
            body = "\n".join(f"◈ <code>{a}</code>" for a in admins) or "<i>none</i>"
            await e.reply(f"{header('admins', '👤')}\n\n" + quote(body, expandable=True),
                          parse_mode="html")
