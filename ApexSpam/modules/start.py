"""Apex Spam X — /start with full fallback chain + logging."""
import logging
import time
from io import BytesIO

from telethon import events

from ApexSpam import HNDLR, START_TIME, CLIENTS
from ApexSpam.ui import header, quote, divider, link_user, footer, safe_format
from ApexSpam.buttons import ib, ub
from models.bot_settings import get_value

log = logging.getLogger("ApexSpam.start")

DEFAULT_CAPTION = "{header}\n\n{greet}\n\n{q1}\n\n{q2}\n\n{meta}"


def _buttons():
    return [
        [ib("⚡  C O M M A N D S", b"help_back", "primary")],
        [ib("📖 About", b"about_btn", "primary"), ib("🛡️ Status", b"status_btn", "success")],
        [ub("📢 Channel", "https://t.me/ApexSpamXSupport", "primary"),
         ub("💬 Support", "https://t.me/ApexSpamXSupport", "primary")],
    ]


async def _build(e, bot_username):
    up = int(time.time() - START_TIME)
    h, r = divmod(up, 3600)
    m, s = divmod(r, 60)
    tpl = None
    try:
        tpl = await get_value("start_caption")
    except Exception as ex:
        log.warning(f"get_value(start_caption): {ex}")

    text = safe_format(
        tpl if isinstance(tpl, str) and tpl.strip() else DEFAULT_CAPTION,
        header=header("apex spam x", "⚡"),
        greet=f"Hey {link_user(e.sender_id, e.sender.first_name or 'User')} 👋",
        q1=quote("<i>Welcome to the ultimate raid engine.</i>"),
        q2=quote(
            f"◈ <b>Prefix</b> : <code>{HNDLR}</code>\n"
            f"◈ <b>Uptime</b> : <code>{h}h {m}m {s}s</code>\n"
            f"◈ <b>Status</b> : <b>✅ Online</b>"
        ),
        meta=f"{divider()}\n<i>Tap below to explore</i> 👇",
    )
    return text.strip() or "⚡ <b>Apex Spam X</b> — online"


async def _send(e, text):
    # Level 1: photo + caption
    try:
        pic = await get_value("start_pic")
        ext = await get_value("start_pic_ext") or "jpg"
        if pic:
            stream = BytesIO(bytes(pic))
            stream.name = f"apex_start.{ext}"
            log.info(f"start:L1 photo {len(pic)}B")
            await e.reply(text, file=stream, buttons=_buttons(), parse_mode="html")
            log.info("start:L1 photo OK")
            return
    except Exception as ex:
        log.exception(f"start:L1 photo failed: {ex}")

    # Level 2: HTML text
    try:
        log.info("start:L2 HTML text")
        await e.reply(text, buttons=_buttons(), parse_mode="html")
        log.info("start:L2 text OK")
        return
    except Exception as ex:
        log.exception(f"start:L2 HTML failed: {ex}")

    # Level 3: plain text
    try:
        log.info("start:L3 plain fallback")
        await e.reply("Apex Spam X is online. Use /help to explore.")
        log.info("start:L3 plain OK")
    except Exception as ex:
        log.exception(f"start:L3 plain failed: {ex}")


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=r"^/start(?:@\w+)?(?:\s|$)"))
        async def start(e):
            try:
                log.info(f"START-HIT uid={e.sender_id} chat={e.chat_id} priv={e.is_private}")
            except Exception:
                pass

            try:
                me = await e.client.get_me()
                username = me.username or "bot"
            except Exception as ex:
                log.exception(f"start:get_me failed: {ex}")
                username = "bot"

            if not e.is_private:
                try:
                    await e.reply(f"👋 DM me to start — @{username}")
                except Exception as ex:
                    log.exception(f"start:group reply failed: {ex}")
                return

            try:
                text = await _build(e, username)
            except Exception as ex:
                log.exception(f"start:build failed: {ex}")
                text = "⚡ <b>Apex Spam X</b> — online"

            await _send(e, text)

        @c.on(events.CallbackQuery(data=b"about_btn"))
        async def about(e):
            try:
                me = await e.client.get_me()
                text = (
                    f"{header('about', '⚡')}\n\n"
                    + quote(
                        f"◈ <b>Name</b>     : <code>Apex Spam X</code>\n"
                        f"◈ <b>Bot</b>      : @{me.username}\n"
                        f"◈ <b>Prefix</b>   : <code>{HNDLR}</code>\n"
                        f"◈ <b>Engine</b>   : <code>Telethon</code>\n"
                        f"◈ <b>Database</b> : <code>MongoDB</code>"
                    )
                    + "\n\n"
                    + quote("👑 <b>Developer</b> : <b>@oyevipthoma88</b>")
                    + f"\n{footer()}"
                )
                await e.edit(text, buttons=[[ib("« Back", b"start_back", "primary")]], parse_mode="html")
            except Exception as ex:
                log.exception(f"about failed: {ex}")
                try: await e.answer("Error", alert=True)
                except Exception: pass

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
                        f"◈ <b>Status</b> : <b>✅ Online</b>\n"
                        f"◈ <b>Engine</b> : <code>Healthy</code>"
                    )
                    + f"\n{footer()}"
                )
                await e.edit(text, buttons=[[ib("« Back", b"start_back", "primary")]], parse_mode="html")
            except Exception as ex:
                log.exception(f"status failed: {ex}")
                try: await e.answer("Error", alert=True)
                except Exception: pass

        @c.on(events.CallbackQuery(data=b"start_back"))
        async def back(e):
            try:
                me = await e.client.get_me()
                await e.edit(await _build(e, me.username or "bot"), buttons=_buttons(), parse_mode="html")
            except Exception as ex:
                log.exception(f"back failed: {ex}")
                try: await e.answer("Error", alert=True)
                except Exception: pass
