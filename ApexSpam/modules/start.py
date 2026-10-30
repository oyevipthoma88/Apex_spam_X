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

BUTTONS = [
    [ib("⚡  C O M M A N D S", b"help_back", "primary")],
    [ib("📖 About", b"about_btn", "primary"), ib("🛡️ Status", b"status_btn", "success")],
    [ub("📢 Channel", "https://t.me/ApexSpamXSupport", "primary"),
     ub("💬 Support", "https://t.me/ApexSpamXSupport", "primary")],
]


def _fallback():
    return (
        f"{header('apex spam x', '⚡')}\n\n"
        + quote("<i>Bot is online.</i>\nUse <code>/help</code>")
    )


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
            f"◈ <b>Prefix</b> : <code>{HNDLR}</code>\n"
            f"◈ <b>Uptime</b> : <code>{h}h {m}m {s}s</code>\n"
            f"◈ <b>Status</b> : <b>✅ Online</b>"
        ),
        meta=f"{divider()}\n<i>Tap below to explore</i> 👇",
    )
    return text.strip() or _fallback()


async def _send(e, text):
    pic = ext = None
    try:
        pic = await get_value("start_pic")
        ext = await get_value("start_pic_ext") or "jpg"
    except Exception as ex:
        log.exception(f"start: settings read failed: {ex}")

    if pic:
        try:
            stream = BytesIO(bytes(pic))
            stream.name = f"apex_start.{ext}"
            await e.reply(text, file=stream, buttons=BUTTONS, parse_mode="html")
            return
        except Exception as ex:
            log.exception(f"start: photo send failed: {ex}")

    try:
        await e.reply(text, buttons=BUTTONS, parse_mode="html")
    except Exception as ex:
        log.exception(f"start: text send failed: {ex}")
        try:
            await e.reply(_fallback(), buttons=BUTTONS, parse_mode="html")
        except Exception:
            await e.reply("Apex Spam X — online ✅")


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=r"^/start(?:@\w+)?(?:\s|$)"))
        async def start(e):
            log.info(f"/start hit uid={e.sender_id} chat={e.chat_id} private={e.is_private}")
            try:
                me = await e.client.get_me()
                if not e.is_private:
                    await e.reply(f"👋 DM me to start — @{me.username or 'bot'}")
                    return
                await _send(e, await _build(e, me.username or "bot"))
            except Exception as ex:
                log.exception(f"start failed: {ex}")
                try:
                    await e.reply("⚡ Apex Spam X is online. Use /help")
                except Exception:
                    pass

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
                await e.answer("Something went wrong", alert=True)

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
                await e.answer("Something went wrong", alert=True)

        @c.on(events.CallbackQuery(data=b"start_back"))
        async def back(e):
            try:
                me = await e.client.get_me()
                await e.edit(await _build(e, me.username or "bot"), buttons=BUTTONS, parse_mode="html")
            except Exception as ex:
                log.exception(f"back failed: {ex}")
                await e.answer("Something went wrong", alert=True)
