"""Apex Spam X — paged owner panel (error-safe)."""
import logging

from telethon import events
from telethon.tl.functions.bots import SetBotInfoRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest

from ApexSpam import (
    HNDLR, OWNER_ID, CLIENTS, HEROKU_APP_NAME, HEROKU_API_KEY,
    USER_SESSION, API_ID, API_HASH,
)
from ApexSpam import respond
from ApexSpam.ui import bread, quote, kv, pill, table, footer
from ApexSpam.buttons import ib, copy_btn
from models.whitelist import list_gcs
from models.sudo import all_records
from models.admins import list_admins

log = logging.getLogger("ApexSpam.owner")
PENDING = {}


async def _apply_name(name):
    """Telegram allows styled Unicode — must NOT pass `bot=` when called as bot."""
    clean = name.strip()[:64]
    if not clean:
        return 0, "", False
    ok = 0
    for c in CLIENTS:
        uname = "?"
        try:
            me = await c.get_me()
            uname = me.username or "?"
            # As a BOT: do NOT pass `bot=` (that's for user accounts)
            await c(SetBotInfoRequest(lang_code="", name=clean))
            # Force peer cache refresh
            try:
                from telethon.tl.functions.users import GetUsersRequest
                from telethon.tl.types import InputUserSelf
                await c(GetUsersRequest([InputUserSelf()]))
            except Exception:
                pass
            ok += 1
            log.info(f"name set @{uname} -> {clean!r}")
        except Exception as ex:
            log.warning(f"name fail @{uname}: {type(ex).__name__}: {ex}")
    return ok, clean, False


async def _apply_bio(bio):
    clean = bio.strip()[:120]
    if not clean:
        return 0, "", False
    ok = 0
    for c in CLIENTS:
        uname = "?"
        try:
            me = await c.get_me()
            uname = me.username or "?"
            await c(SetBotInfoRequest(lang_code="", about=clean))
            ok += 1
            log.info(f"bio set @{uname} -> {clean[:30]!r}")
        except Exception as ex:
            log.warning(f"bio fail @{uname}: {type(ex).__name__}: {ex}")
    return ok, clean, False


async def _apply_pic(data):
    if not USER_SESSION:
        return -1
    try:
        from telethon import TelegramClient
        from telethon.sessions import StringSession
        uc = TelegramClient(StringSession(USER_SESSION), API_ID, API_HASH)
        await uc.connect()
        ok = 0
        for c in CLIENTS:
            try:
                me = await c.get_me()
                up = await uc.upload_file(data)
                await uc(UploadProfilePhotoRequest(fallback=True, bot=me.username, file=up))
                ok += 1
            except Exception:
                pass
        await uc.disconnect()
        return ok
    except Exception:
        return -1


def _main():
    text = (
        f"{bread('owner', 'panel')}\n\n"
        + quote(f"{pill(f'{len(CLIENTS)} bots', 'ok')}\n{pill('online', 'ok')}", expandable=True)
        + f"\n{footer()}"
    )
    rows = [
        [ib("🎨 Appearance", b"opx:look", "primary"),
         ib("🛡️ Access", b"opx:acc", "primary")],
        [ib("⚙️ System", b"opx:sys", "primary"),
         ib("✖ Close", b"opx:close", "danger")],
    ]
    return text, rows


def _look():
    text = (
        f"{bread('owner', 'appearance')}\n\n"
        + quote("Update every connected bot.", expandable=True)
        + f"\n{footer()}"
    )
    rows = [
        [ib("✏️ Name", b"op_setname", "primary"),
         ib("📝 Bio", b"op_setbio", "primary")],
        [ib("🖼️ Photo", b"op_setpic", "primary"),
         ib("🎨 Start Pic", b"op_setstartpic", "success")],
        [ib("« Back", b"opx:main", "primary")],
    ]
    return text, rows


def _acc():
    text = (
        f"{bread('owner', 'access')}\n\n"
        + quote("Sudo chain: you can remove only users you added.", expandable=True)
        + f"\n{footer()}"
    )
    rows = [
        [ib("👤 + Admin", b"op_addadmin", "success"),
         ib("🚫 − Admin", b"op_deladmin", "danger")],
        [ib("🛡️ + Sudo", b"op_addsudo", "success"),
         ib("⚔️ − Sudo", b"op_delsudo", "danger")],
        [ib("📋 Lists", b"opx:lists", "primary"),
         ib("« Back", b"opx:main", "primary")],
    ]
    return text, rows


def _sys():
    text = (
        f"{bread('owner', 'system')}\n\n"
        + quote("Restart or fetch logs.", expandable=True)
        + f"\n{footer()}"
    )
    rows = [
        [ib("🔄 Restart", b"op_update", "primary"),
         ib("📜 Logs", b"op_logs", "primary")],
        [ib("« Back", b"opx:main", "primary")],
    ]
    return text, rows


async def _lists():
    gcs = await list_gcs()
    admins = await list_admins()
    sudos = await all_records()
    g_rows = [[g] for g in gcs[:10]] or [["none"]]
    a_rows = [[a] for a in admins[:10]] or [["none"]]
    s_rows = [[x["user_id"], x.get("source", "mongo")] for x in sudos[:10]] or [["none", "-"]]
    body = (
        f"{pill(f'GCs {len(gcs)}', 'info')}\n"
        + table(["GC"], g_rows)
        + f"\n{pill(f'Admins {len(admins)}', 'info')}\n"
        + table(["ADMIN"], a_rows)
        + f"\n{pill(f'Sudos {len(sudos)}', 'info')}\n"
        + table(["SUDO", "SRC"], s_rows)
    )
    ids = "\n".join(str(x["user_id"]) for x in sudos[:20])
    rows = []
    if ids:
        cb = copy_btn("📋 Copy sudo IDs", ids)
        if cb:
            rows.append([cb])
    rows.append([ib("« Back", b"opx:acc", "primary")])
    return f"{bread('owner', 'lists')}\n\n{body}", rows


async def _page(action):
    if action == "look":
        return _look()
    if action == "acc":
        return _acc()
    if action == "sys":
        return _sys()
    if action == "lists":
        return await _lists()
    return _main()


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=r"^[\.!/]dev(?: |$)"))
        async def dev(e):
            if e.sender_id != OWNER_ID:
                return
            text, rows = _main()
            await e.reply(text, buttons=rows, parse_mode="html")

        @c.on(events.CallbackQuery(data=b"owner_panel"))
        async def open_panel(e):
            log.info(f"owner_panel from {e.sender_id}")
            if e.sender_id != OWNER_ID:
                return await respond.ack(e, "Owner only", True)
            try:
                text, rows = _main()
                await respond.edit(e, text, rows)
            except Exception as ex:
                log.exception(f"owner_panel failed: {ex}")
                await respond.ack(e, f"Error: {str(ex)[:40]}", True)

        @c.on(events.CallbackQuery(pattern=r"opx:(\w+)"))
        async def opx(e):
            if e.sender_id != OWNER_ID:
                return await respond.ack(e, "Owner only", True)
            try:
                action = e.pattern_match.group(1)
                if isinstance(action, bytes):
                    action = action.decode()
                log.info(f"opx action={action}")
                if action == "close":
                    await respond.ack(e)
                    try:
                        await e.delete()
                    except Exception:
                        pass
                    return
                await respond.ack(e)
                text, rows = await _page(action)
                await respond.edit(e, text, rows)
            except Exception as ex:
                log.exception(f"opx failed: {ex}")
                await respond.ack(e, f"Error: {str(ex)[:40]}", True)

        @c.on(events.CallbackQuery(data=b"op_setname"))
        async def cb_setname(e):
            if e.sender_id != OWNER_ID:
                return await respond.ack(e, "Owner only", True)
            try:
                m = await e.edit(
                    f"{bread('owner', 'set name')}\n\n"
                    + quote("Reply with <b>plain text</b> name.\n"
                            "<i>Telegram bot names cannot use styled font.</i>"),
                    parse_mode="html",
                )
                PENDING[e.chat_id] = ("setname", m.id)
                await respond.ack(e, "Reply with name")
            except Exception as ex:
                log.exception(f"cb_setname: {ex}")

        @c.on(events.CallbackQuery(data=b"op_setbio"))
        async def cb_setbio(e):
            if e.sender_id != OWNER_ID:
                return await respond.ack(e, "Owner only", True)
            try:
                m = await e.edit(
                    f"{bread('owner', 'set bio')}\n\n"
                    + quote("Reply with <b>plain text</b> bio."),
                    parse_mode="html",
                )
                PENDING[e.chat_id] = ("setbio", m.id)
                await respond.ack(e, "Reply with bio")
            except Exception as ex:
                log.exception(f"cb_setbio: {ex}")

        @c.on(events.CallbackQuery(data=b"op_setpic"))
        async def cb_setpic(e):
            if e.sender_id != OWNER_ID:
                return await respond.ack(e, "Owner only", True)
            try:
                m = await e.edit(
                    f"{bread('owner', 'set photo')}\n\n"
                    + quote("Reply with a photo."),
                    parse_mode="html",
                )
                PENDING[e.chat_id] = ("setpic", m.id)
                await respond.ack(e, "Reply with photo")
            except Exception as ex:
                log.exception(f"cb_setpic: {ex}")

        @c.on(events.CallbackQuery(data=b"op_setstartpic"))
        async def cb_setstartpic(e):
            if e.sender_id != OWNER_ID:
                return await respond.ack(e, "Owner only", True)
            try:
                m = await e.edit(
                    f"{bread('owner', 'set start pic')}\n\n"
                    + quote("Reply with a photo.\nStays saved after restart."),
                    parse_mode="html",
                )
                PENDING[e.chat_id] = ("setstartpic", m.id)
                await respond.ack(e, "Reply with photo")
            except Exception as ex:
                log.exception(f"cb_setstartpic: {ex}")

        @c.on(events.NewMessage())
        async def pending(e):
            if e.sender_id != OWNER_ID:
                return
            if e.text and e.text.startswith((".", "!", "/")):
                return
            entry = PENDING.get(e.chat_id)
            if not entry:
                return
            action, prompt_id = entry
            if e.reply_to_msg_id != prompt_id:
                return
            PENDING.pop(e.chat_id, None)
            try:
                if action == "setname" and e.text:
                    ok, clean, stripped = await _apply_name(e.text[:64])
                    body = (
                        f"{pill('Updated', 'ok') if ok else pill('Failed', 'bad')}\n"
                        f"{kv('Applied', clean)}\n"
                        f"{kv('Count', f'{ok}/{len(CLIENTS)}')}"
                    )
                    if not ok:
                        body += "\n\n<i>⚠️ Name update failed — check Heroku logs.</i>"
                    await e.reply(f"{bread('owner', 'name')}\n\n" + quote(body),
                                  parse_mode="html")
                elif action == "setbio" and e.text:
                    ok, clean, stripped = await _apply_bio(e.text[:140])
                    body = (
                        f"{pill('Updated', 'ok') if ok else pill('Failed', 'bad')}\n"
                        f"{kv('Applied', clean)}\n"
                        f"{kv('Count', f'{ok}/{len(CLIENTS)}')}"
                    )
                    if not ok:
                        body += "\n\n<i>⚠️ Bio update failed.</i>"
                    await e.reply(f"{bread('owner', 'bio')}\n\n" + quote(body),
                                  parse_mode="html")
                elif action in ("setpic", "setstartpic"):
                    if not e.photo and not (e.document and "image" in (e.document.mime_type or "")):
                        return await e.reply("❌ Not a photo.", parse_mode="html")
                    data = await e.download_media(file=bytes)
                    if not data:
                        return await e.reply("❌ Download failed.", parse_mode="html")
                    if action == "setstartpic":
                        from ApexSpam.modules.apexpic import _detect_ext
                        from models.bot_settings import set_value
                        ext = _detect_ext(data)
                        await set_value("start_pic", data)
                        await set_value("start_pic_ext", ext)
                        await e.reply(
                            f"{bread('owner', 'start pic')}\n\n"
                            + quote(f"{pill('Saved', 'ok')}\n{kv('Size', f'{len(data)//1024} KB')}"),
                            parse_mode="html",
                        )
                    else:
                        ok = await _apply_pic(data)
                        msg = pill('Updated', 'ok') if ok != -1 else pill('USER_SESSION missing', 'bad')
                        await e.reply(
                            f"{bread('owner', 'photo')}\n\n"
                            + quote(f"{msg}\n{kv('Count', ok if ok != -1 else 'n/a')}"),
                            parse_mode="html",
                        )
            except Exception as ex:
                log.exception(f"pending {action}: {ex}")

        @c.on(events.CallbackQuery(data=b"op_addadmin"))
        async def addadmin_cb(e):
            if e.sender_id != OWNER_ID:
                return await respond.ack(e, "Owner only", True)
            await respond.ack(e, "Send .addadmin ID")

        @c.on(events.CallbackQuery(data=b"op_deladmin"))
        async def deladmin_cb(e):
            if e.sender_id != OWNER_ID:
                return await respond.ack(e, "Owner only", True)
            await respond.ack(e, "Send .deladmin ID")

        @c.on(events.CallbackQuery(data=b"op_addsudo"))
        async def addsudo_cb(e):
            if e.sender_id != OWNER_ID:
                return await respond.ack(e, "Owner only", True)
            await respond.ack(e, "Send .addsudo ID")

        @c.on(events.CallbackQuery(data=b"op_delsudo"))
        async def delsudo_cb(e):
            if e.sender_id != OWNER_ID:
                return await respond.ack(e, "Owner only", True)
            await respond.ack(e, "Send .delsudo ID")

        @c.on(events.CallbackQuery(data=b"op_update"))
        async def update_cb(e):
            if e.sender_id != OWNER_ID:
                return await respond.ack(e, "Owner only", True)
            if not HEROKU_APP_NAME or not HEROKU_API_KEY:
                return await respond.ack(e, "Heroku not configured", True)
            try:
                import heroku3
                app = heroku3.from_key(HEROKU_API_KEY).app(HEROKU_APP_NAME)
                await respond.ack(e, "Restarting…")
                app.restart()
            except Exception as ex:
                await respond.ack(e, str(ex)[:40], True)

        @c.on(events.CallbackQuery(data=b"op_logs"))
        async def logs_cb(e):
            if e.sender_id != OWNER_ID:
                return await respond.ack(e, "Owner only", True)
            await respond.ack(e, "Send .axlogs", True)

        @c.on(events.NewMessage(pattern=r"^[\.!/]setname(?: |$)"))
        async def setname(e):
            if e.sender_id != OWNER_ID:
                return
            parts = e.text.split(maxsplit=1)
            if len(parts) < 2:
                return await e.reply("<code>.setname New Name</code>", parse_mode="html")
            ok, clean, stripped = await _apply_name(parts[1][:64])
            body = (
                f"{pill('Updated', 'ok') if ok else pill('Failed', 'bad')}\n"
                f"{kv('Applied', clean)}\n"
                f"{kv('Count', f'{ok}/{len(CLIENTS)}')}"
            )
            if not ok:
                body += "\n\n<i>⚠️ Name update failed.</i>"
            await e.reply(f"{bread('owner', 'name')}\n\n" + quote(body), parse_mode="html")

        @c.on(events.NewMessage(pattern=r"^[\.!/]setbio(?: |$)"))
        async def setbio(e):
            if e.sender_id != OWNER_ID:
                return
            parts = e.text.split(maxsplit=1)
            if len(parts) < 2:
                return await e.reply("<code>.setbio Bio</code>", parse_mode="html")
            ok, clean, stripped = await _apply_bio(parts[1][:140])
            body = (
                f"{pill('Updated', 'ok') if ok else pill('Failed', 'bad')}\n"
                f"{kv('Applied', clean)}\n"
                f"{kv('Count', f'{ok}/{len(CLIENTS)}')}"
            )
            if not ok:
                body += "\n\n<i>⚠️ Bio update failed.</i>"
            await e.reply(f"{bread('owner', 'bio')}\n\n" + quote(body), parse_mode="html")

        @c.on(events.NewMessage(pattern=r"^[\.!/]setbotpic(?: |$)"))
        async def setbotpic(e):
            if e.sender_id != OWNER_ID:
                return
            if not e.reply_to_msg_id:
                return await e.reply("Reply to a photo.", parse_mode="html")
            r = await e.get_reply_msg if False else await e.get_reply_message()
            if not r.photo and not (r.document and "image" in (r.document.mime_type or "")):
                return await e.reply("❌ Not a photo.", parse_mode="html")
            data = await r.download_media(file=bytes)
            if not data:
                return await e.reply("❌ Download failed.", parse_mode="html")
            ok = await _apply_pic(data)
            msg = pill('Updated', 'ok') if ok != -1 else pill('USER_SESSION missing', 'bad')
            await e.reply(f"{bread('owner', 'photo')}\n\n" + quote(f"{msg}"), parse_mode="html")
