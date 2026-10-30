"""Apex Spam X — /start (multi-prefix, owner panel, error-safe)."""
import logging
import time
from io import BytesIO

from telethon import events

from ApexSpam import HNDLR, START_TIME, CLIENTS, OWNER_ID
from ApexSpam.ui import header, quote, divider, link_user, footer, safe_format
from ApexSpam.buttons import ib
from models.bot_settings import get_value

log = logging.getLogger("ApexSpam.start")

DEFAULT_CAPTION = "{header}\n\n{greet}\n\n{q1}\n\n{q2}\n\n{meta}"


def _buttons(uid=0):
    rows = [
        [ib("⚡  C O M M A N D S", b"help_back", "primary")],
        [ib("📖 About", b"about_btn", "primary"),
         ib("🛡️ Status", b"status_btn", "success")],
    ]
    if uid == OWNER_ID:
        rows.append([ib("👑 Owner Panel", b"owner_panel", "danger")])
    return rows


async def _build(e, bot_username):
    up = int(time.time() - START_TIME)
    h, r = divmod(up, 3600)
    m, s = divmod(r, 60)
    try:
        tpl = await get_value("start_caption")
    except Exception:
        tpl = None
    text = safe_format(
        tpl if isinstance(tpl, str) and tpl.strip() else DEFAULT_CAPTION,
        header=header("apex spam x", "⚡"),
        greet=f"Hey {link_user(e.sender_id, e.sender.first_name or 'User')} 👋",
        q1=quote("<i>Welcome to the ultimate raid engine.</i>"),
        q2=quote(
            f"◈ <b>Prefix</b> : <code>{HNDLR} ! /</code>\n"
            f"◈ <b>Bot</b>    : <code>@{bot_username}</code>\n"
            f"◈ <b>Uptime</b> : <code>{h}h {m}m {s}s</code>\n"
            f"◈ <b>Status</b> : <b>✅ Online</b>"
        ),
        meta=f"{divider()}\n<i>Tap below to explore</i> 👇",
    )
    return text.strip() or "⚡ <b>Apex Spam X</b> — online"


async def _send(e, text):
    try:
        pic = await get_value("start_pic")
        ext = await get_value("start_pic_ext") or "jpg"
        if pic:
            stream = BytesIO(bytes(pic))
            stream.name = f"apex_start.{ext}"
            await e.reply(text, file=stream,
                          buttons=_buttons(e.sender_id), parse_mode="html")
            return
    except Exception as ex:
        log.exception(f"pic failed: {ex}")
    try:
        await e.reply(text, buttons=_buttons(e.sender_id), parse_mode="html")
    except Exception as ex:
        log.exception(f"text failed: {ex}")
        try:
            await e.reply("⚡ Apex Spam X — online. /help")
        except Exception:
            pass


def register():
    log.info(f"registering start.py | HNDLR={HNDLR!r} | clients={len(CLIENTS)}")

    for c in CLIENTS:
        # /start with multi-prefix
        @c.on(events.NewMessage(pattern=rf"^[\.!/]start(?:@\w+)?(?:\s|$)"))
        async def start(e):
            log.info(f"START-HIT uid={e.sender_id} priv={e.is_private}")
            try:
                me = await e.client.get_me()
                username = me.username or "bot"
            except Exception:
                username = "bot"

            if not e.is_private:
                try:
                    await e.reply(f"👋 DM me to start — @{username}")
                except Exception:
                    pass
                return

            try:
                await _send(e, await _build(e, username))
            except Exception as ex:
                log.exception(f"start: {ex}")

        @c.on(events.CallbackQuery(data=b"about_btn"))
        async def about(e):
            try:
                me = await e.client.get_me()
                text = (
                    f"{header('about', '⚡')}\n\n"
                    + quote(
                        f"◈ <b>Name</b>     : <code>Apex Spam X</code>\n"
                        f"◈ <b>Bot</b>      : @{me.username}\n"
                        f"◈ <b>Prefix</b>   : <code>{HNDLR} ! /</code>\n"
                        f"◈ <b>Engine</b>   : <code>Telethon</code>\n"
                        f"◈ <b>Database</b> : <code>MongoDB</code>"
                    )
                    + "\n\n" + quote("👑 <b>Powered by Apex Spam X</b>")
                    + f"\n{footer()}"
                )
                await e.edit(text, buttons=[[ib("« Back", b"start_back", "primary")]],
                             parse_mode="html")
            except Exception:
                pass

        @c.on(events.CallbackQuery(data=b"status_btn"))
        async def status(e):
            try:
                up = int(time.time() - START_TIME)
                h, r = divmod(up, 3600)
                m, s = divmod(r, 60)
                text = (
                    f"{header('status', '🛡️')}\n\n"
                    + quote(
                        f"◈ <b>Uptime</b> : <code>{h}h {m}m {s}s</code>\n"
                        f"◈ <b>Status</b> : <b>✅ Online</b>"
                    )
                    + f"\n{footer()}"
                )
                await e.edit(text, buttons=[[ib("« Back", b"start_back", "primary")]],
                             parse_mode="html")
            except Exception:
                pass

        @c.on(events.CallbackQuery(data=b"owner_panel"))
        async def op(e):
            if e.sender_id != OWNER_ID:
                return await e.answer("Owner only", alert=True)
            try:
                from ApexSpam.modules.owner_panel import _text as t, _buttons as b
                await e.edit(t(), buttons=b(), parse_mode="html")
            except Exception:
                await e.answer("Error", alert=True)

        @c.on(events.CallbackQuery(data=b"start_back"))
        async def back(e):
            try:
                me = await e.client.get_me()
                await e.edit(await _build(e, me.username or "bot"),
                             buttons=_buttons(e.sender_id), parse_mode="html")
            except Exception:
                pass
