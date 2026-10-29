from io import BytesIO
import time

from telethon import events, Button
from ApexSpam import HNDLR, START_TIME, CLIENTS
from ApexSpam.ui import header, quote, kv, divider, link_user
from models.bot_settings import get_value

DEFAULT_CAPTION = "{header}\n\n{greet}\n\n{q1}\n\n{q2}\n\n{meta}"

BUTTONS = [
    [Button.inline("⚡  C O M M A N D S", data="help_back")],
    [Button.inline("📖 About", data="about_btn"), Button.inline("🛡️ Status", data="status_btn")],
    [Button.url("📢 Channel", "https://t.me/ApexSpamXSupport"),
     Button.url("💬 Support", "https://t.me/ApexSpamXSupport")],
]


async def _build(e, bot_username: str) -> str:
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
        meta=divider() + "\n<i>Tap below to explore</i> 👇",
    )


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=r"/start(?: |$)"))
        async def start(e):
            if not e.is_private:
                return
            me = await e.client.get_me()
            text = await _build(e, me.username or "bot")
            pic = await get_value("start_pic")
            try:
                if pic:
                    await e.reply(file=BytesIO(pic), caption=text, buttons=BUTTONS, parse_mode="html")
                else:
                    await e.reply(text, buttons=BUTTONS, parse_mode="html")
            except Exception:
                await e.reply(text, buttons=BUTTONS, parse_mode="html")

        @c.on(events.CallbackQuery(data=b"about_btn"))
        async def about(e):
            me = await e.client.get_me()
            text = (
                f"{header('about', '⚡')}\n\n"
                + quote(
                    f"◈ <b>Name</b>     :  <code>Apex Spam X</code>\n"
                    f"◈ <b>Bot</b>      :  @{me.username}\n"
                    f"◈ <b>Prefix</b>   :  <code>{HNDLR}</code>\n"
                    f"◈ <b>Engine</b>   :  <code>Telethon</code>\n"
                    f"◈ <b>Database</b> :  <code>MongoDB</code>\n"
                    f"◈ <b>Deploy</b>   :  <code>Heroku</code>",
                    expandable=True,
                )
                + "\n\n"
                + quote("👑 <b>Developer</b> : <b>@oyevipthoma88</b>")
            )
            await e.edit(text, buttons=[[Button.inline("« Back", data="start_back")]], parse_mode="html")

        @c.on(events.CallbackQuery(data=b"status_btn"))
        async def status(e):
            up = int(time.time() - START_TIME)
            h, r = divmod(up, 3600)
            m, s = divmod(r, 60)
            text = (
                f"{header('status', '🛡️')}\n\n"
                + quote(
                    f"◈ <b>Uptime</b>  :  <code>{h}h {m}m {s}s</code>\n"
                    "◈ <b>Status</b>  :  <b>✅ Online</b>\n"
                    "◈ <b>Engine</b>  :  <code>Healthy</code>",
                    expandable=True,
                )
            )
            await e.edit(text, buttons=[[Button.inline("« Back", data="start_back")]], parse_mode="html")

        @c.on(events.CallbackQuery(data=b"start_back"))
        async def back(e):
            me = await e.client.get_me()
            text = await _build(e, me.username or "bot")
            await e.edit(text, buttons=BUTTONS, parse_mode="html")
