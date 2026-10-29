import logging
import time
from io import BytesIO
from telethon import events
from ApexSpam import HNDLR, START_TIME, CLIENTS
from ApexSpam.ui import header, quote, kv, divider, link_user, footer, BRAND
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


async def _build(e, bot_username):
    up = int(time.time() - START_TIME)
    h, r = divmod(up, 3600)
    m, s = divmod(r, 60)
    tpl = await get_value("start_caption") or DEFAULT_CAPTION
    return tpl.format(
        header=header("apex spam x", "⚡"),
        greet=f"Hey {link_user(e.sender_id, e.sender.first_name or 'User')} 👋",
        q1=quote("<i>Welcome to the ultimate raid engine.</i>"),
        q2=quote(
            f"◈ <b>Prefix</b>  :  <code>{HNDLR}</code>\n"
            f"◈ <b>Bot</b>     :  @{bot_username}\n"
            f"◈ <b>Uptime</b>  :  <code>{h}h {m}m {s}s</code>\n"
            f"◈ <b>Status</b>  :  <b>✅ Online</b>",
            expandable=True,
        ),
        meta=divider() + f"\n<i>Tap below to explore</i> 👇\n{footer()}",
    )


async def _send(e, text):
    pic = ext = None
    try:
        pic = await get_value("start_pic")
        ext = await get_value("start_pic_ext") or "jpg"
    except Exception:
        log.exception("start: mongo read failed")
    if pic:
        try:
            stream = BytesIO(bytes(pic))
            stream.name = f"apex_start.{ext}"
            await e.reply(text, file=stream, buttons=BUTTONS, parse_mode="html")
            return
        except Exception:
            log.exception("start: photo failed, fallback text")
    await e.reply(text, buttons=BUTTONS, parse_mode="html")


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=r"/start(?: |$)"))
        async def start(e):
            if not e.is_private: return
            me = await e.client.get_me()
            await _send(e, await _build(e, me.username or "bot"))

        @c.on(events.CallbackQuery(data=b"about_btn"))
        async def about(e):
            me = await e.client.get_me()
            text = (
                f"{header('about', '⚡')}\n\n"
                + quote(
                    f"◈ <b>Name</b>     :  <code>{BRAND}</code>\n"
                    f"◈ <b>Bot</b>      :  @{me.username}\n"
                    f"◈ <b>Prefix</b>   :  <code>{HNDLR}</code>\n"
                    f"◈ <b>Engine</b>   :  <code>Telethon</code>\n"
                    f"◈ <b>Database</b> :  <code>MongoDB</code>\n"
                    f"◈ <b>Deploy</b>   :  <code>Heroku</code>",
                    expandable=True,
                )
                + "\n\n" + quote("👑 <b>Developer</b> : <b>@oyevipthoma88</b>")
                + f"\n\n{footer()}"
            )
            await e.edit(text, buttons=[[ib("« Back", b"start_back", "primary")]], parse_mode="html")

        @c.on(events.CallbackQuery(data=b"status_btn"))
        async def status(e):
            up = int(time.time() - START_TIME)
            h, r = divmod(up, 3600)
            m, s = divmod(r, 60)
            text = (
                f"{header('status', '🛡️')}\n\n"
                + quote(f"{kv('Uptime', f'{h}h {m}m {s}s')}\n{kv('Status', '✅ Online')}\n{kv('Engine', 'Healthy')}", expandable=True)
                + f"\n\n{footer()}"
            )
            await e.edit(text, buttons=[[ib("« Back", b"start_back", "primary")]], parse_mode="html")

        @c.on(events.CallbackQuery(data=b"start_back"))
        async def back(e):
            me = await e.client.get_me()
            await e.edit(await _build(e, me.username or "bot"), buttons=BUTTONS, parse_mode="html")
