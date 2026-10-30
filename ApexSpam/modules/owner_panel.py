"""Apex Spam X — paged owner panel."""
import logging
from telethon import events
from telethon.tl.functions.bots import SetBotInfoRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest

from ApexSpam import (
    HNDLR, OWNER_ID, CLIENTS, HEROKU_APP_NAME, HEROKU_API_KEY,
    USER_SESSION, API_ID, API_HASH,
)
from ApexSpam import roles, respond
from ApexSpam.ui import bread, quote, kv, pill, table, footer, join_rows
from ApexSpam.buttons import ib, ub, copy_btn, grid, nav
from models.whitelist import add_gc, list_gcs
from models.sudo import add_sudo, remove_sudo, all_records
from models.admins import add_admin, remove_admin, list_admins

log = logging.getLogger("ApexSpam.owner")
PENDING = {}


async def _apply_name(name):
    from ApexSpam.fonts import asciify
    clean = asciify(name)[:64]
    stripped = clean != name
    ok = 0
    for c in CLIENTS:
        try:
            me = await c.get_me()
            await c(SetBotInfoRequest(bot=me.id, lang_code="en", name=clean))
            ok += 1
        except Exception as ex:
            log.warning(f"name fail: {ex}")
    return ok, clean, stripped


async def _apply_bio(bio):
    from ApexSpam.fonts import asciify
    clean = asciify(bio)[:120]
    ok = 0
    for c in CLIENTS:
        try:
            me = await c.get_me()
            await c(SetBotInfoRequest(bot=me.id, lang_code="en", about=clean))
            ok += 1
        except Exception as ex:
            log.warning(f"bio fail: {ex}")
    return ok


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
    body = f"{pill(f'{len(CLIENTS)} bots', 'ok')}\n{pill('online', 'ok')}"
    return (
        f"{bread('owner', 'panel')}\n\n"
        + quote(body, expandable=True)
        + f"\n{footer()}"
    ), [
        [ib("🎨 Appearance", b"opx:look", "primary"),
         ib("🛡️ Access", b"opx:acc", "primary")],
        [ib("⚙️ System", b"opx:sys", "primary"),
         ib("✖ Close", b"opx:close", "danger")],
    ]


def _look():
    return (
        f"{bread('owner', 'appearance')}\n\n"
        + quote("Update every connected bot.", expandable=True)
        + f"\n{footer()}"
    ), [
        [ib("✏️ Name", b"op_setname", "primary"),
         ib("📝 Bio", b"op_setbio", "primary")],
        [ib("🖼️ Photo", b"op_setpic", "primary"),
         ib("🎨 Start Pic", b"op_setstartpic", "success")],
        [ib("« Back", b"opx:main", "primary")],
    ]


def _acc():
    return (
        f"{bread('owner', 'access')}\n\n"
        + quote("Sudo chain: you can remove only users you added.", expandable=True)
        + f"\n{footer()}"
    ), [
        [ib("👤 + Admin", b"op_addadmin", "success"),
         ib("🚫 − Admin", b"op_deladmin", "danger")],
        [ib("🛡️ + Sudo", b"op_addsudo", "success"),
         ib("⚔️ − Sudo", b"op_delsudo", "danger")],
        [ib("📋 Lists", b"opx:lists", "primary"),
         ib("« Back", b"opx:main", "primary")],
    ]


def _sys():
    return (
        f"{bread('owner', 'system')}\n\n"
        + quote("Restart or fetch logs.", expandable=True)
        + f"\n{footer()}"
    ), [
        [ib("🔄 Restart", b"op_update", "primary"),
         ib("📜 Logs", b"op_logs", "primary")],
        [ib("« Back", b"opx:main", "primary")],
    ]


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
    btns = []
    cb = copy_btn("📋 Copy sudo IDs", ids) if ids else None
    if cb:
        btns.append([cb])
    btns.append([ib("« Back", b"opx:acc", "primary")])
    return f"{bread('owner', 'lists')}\n\n{body}", join_rows(btns)


def _text():
    return _main()[0]


def _buttons():
    return _main()[1]


async def _page(action):
    if action == "main":
        return _main()
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

        @c.on(events.CallbackQuery(pattern=r"opx:(\w+)"))
        async def opx(e):
            log.info(f"opx from {e.sender_id} data={e.data!r}")
            if e.sender_id != OWNER_ID:
                return await respond.ack(e, "Owner only", True)
            action = e.pattern_match.group(1)
                if isinstance(action, bytes):
                    action = action.decode()
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

        # ── pending flows ──
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

        @c.on(events.CallbackQuery(data=b"op_setname"))
        async def cb_setname(e):
            if e.sender_id != OWNER_ID:
                return await respond.ack(e, "Owner only", True)
            m = await e.edit(f"{bread('owner', 'set name')}\n\n"
                             + quote("Reply to this message with the new name."),
                             parse_mode="html")
            PENDING[e.chat_id] = ("setname", m.id)
            await respond.ack(e, "Reply with name")

        @c.on(events.CallbackQuery(data=b"op_setbio"))
        async def cb_setbio(e):
            if e.sender_id != OWNER_ID:
                return await respond.ack(e, "Owner only", True)
            m = await e.edit(f"{bread('owner', 'set bio')}\n\n"
                             + quote("Reply to this message with the new bio."),
                             parse_mode="html")
            PENDING[e.chat_id] = ("setbio", m.id)
            await respond.ack(e, "Reply with bio")

        @c.on(events.CallbackQuery(data=b"op_setpic"))
        async def cb_setpic(e):
            if e.sender_id != OWNER_ID:
                return await respond.ack(e, "Owner only", True)
            m = await e.edit(f"{bread('owner', 'set photo')}\n\n"
                             + quote("Reply to this message with a photo."),
                             parse_mode="html")
            PENDING[e.chat_id] = ("setpic", m.id)
            await respond.ack(e, "Reply with photo")

        @c.on(events.CallbackQuery(data=b"op_setstartpic"))
        async def cb_setstartpic(e):
            if e.sender_id != OWNER_ID:
                return await respond.ack(e, "Owner only", True)
            m = await e.edit(f"{bread('owner', 'set start pic')}\n\n"
                             + quote("Reply to this message with a photo.\n"
                                     "It stays saved after restart (MongoDB)."),
                             parse_mode="html")
            PENDING[e.chat_id] = ("setstartpic", m.id)
            await respond.ack(e, "Reply with photo")

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

            if action == "setname" and e.text:
                ok, clean, stripped = await _apply_name(e.text[:64])
                body = (
                    f"{pill('Updated', 'ok') if ok else pill('Failed', 'bad')}\n"
                    f"{kv('Applied', clean)}\n"
                    f"{kv('Count', f'{ok}/{len(CLIENTS)}')}"
                )
                if stripped:
                    body += "\n\n<i>⚠️ Styled characters stripped — Telegram bot names must be plain ASCII.</i>"
                await e.reply(f"{bread('owner', 'name')}\n\n" + quote(body),
                              parse_mode="html")
            elif action == "setbio" and e.text:
                ok = await _apply_bio(e.text[:140])
                await e.reply(f"{bread('owner', 'bio')}\n\n"
                              + quote(f"{pill('Updated', 'ok')}\n{kv('Count', f'{ok}/{len(CLIENTS)}')}"),
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
                    await e.reply(f"{bread('owner', 'start pic')}\n\n"
                                  + quote(f"{pill('Saved', 'ok')}\n{kv('Size', f'{len(data)//1024} KB')}"),
                                  parse_mode="html")
                else:
                    ok = await _apply_pic(data)
                    await e.reply(f"{bread('owner', 'photo')}\n\n"
                                  + quote(f"{pill('Updated', 'ok') if ok != -1 else pill('USER_SESSION missing', 'bad')}"),
                                  parse_mode="html")

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
