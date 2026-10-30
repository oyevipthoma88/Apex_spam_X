"""Apex Spam X — ping + reboot (fast, cached)."""
import time
from telethon import events

from ApexSpam import HNDLR, OWNER_ID, START_TIME, HEROKU_APP_NAME, HEROKU_API_KEY, CLIENTS
from ApexSpam import botinfo, respond
from ApexSpam.ui import bread, quote, kv, footer, pill
from ApexSpam.buttons import ib


def _uptime():
    up = int(time.time() - START_TIME)
    d, r = divmod(up, 86400)
    h, r = divmod(r, 3600)
    m, s = divmod(r, 60)
    return f"{d}d {h}h {m}m" if d else f"{h}h {m}m"


def _card(rtt, username):
    sig = "Excellent" if rtt < 250 else ("Good" if rtt < 600 else "Slow")
    body = (
        f"{pill(sig, 'ok' if rtt < 600 else 'warn')}\n"
        f"{kv('Latency', f'{rtt} ms')}\n"
        f"{kv('Uptime', _uptime())}\n"
        f"{kv('Bot', '@' + username)}"
    )
    return f"{bread('system', 'ping')}\n\n{quote(body, expandable=True)}\n{footer()}"


def _btns():
    return [[ib("🔄 Refresh", b"ping:refresh", "primary")]]


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=r"^[\.!/]ping(?: |$)"))
        async def ping(e):
            t0 = time.time()
            u = await botinfo.username(e.client)
            rtt = round((time.time() - t0) * 1000, 2)
            await e.reply(_card(rtt, u), buttons=_btns(), parse_mode="html")

        @c.on(events.CallbackQuery(data=b"ping:refresh"))
        async def refresh(e):
            await respond.ack(e, "Refreshing…")
            t0 = time.time()
            u = await botinfo.username(e.client)
            rtt = round((time.time() - t0) * 1000, 2)
            await respond.edit(e, _card(rtt, u), buttons=_btns())

        @c.on(events.NewMessage(pattern=r"^[\.!/]reboot(?: |$)"))
        async def reboot(e):
            if e.sender_id != OWNER_ID:
                return
            if not HEROKU_APP_NAME or not HEROKU_API_KEY:
                return await e.reply("⚠️ Reboot not configured.", parse_mode="html")
            try:
                import heroku3
                app = heroku3.from_key(HEROKU_API_KEY).app(HEROKU_APP_NAME)
                await e.reply("♻️ Restarting…", parse_mode="html")
                app.restart()
            except Exception as err:
                await e.reply(f"❌ <code>{err}</code>", parse_mode="html")
