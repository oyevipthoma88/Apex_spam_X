"""Apex Spam X — ping + Heroku reboot."""
import time
from telethon import events
from ApexSpam import HNDLR, OWNER_ID, START_TIME, HEROKU_APP_NAME, HEROKU_API_KEY, CLIENTS
from ApexSpam.ui import title, quote, kv, footer


def _uptime():
    up = int(time.time() - START_TIME)
    d, r = divmod(up, 86400)
    h, r = divmod(r, 3600)
    m, s = divmod(r, 60)
    return f"{d}d {h}h {m}m" if d else f"{h}h {m}m"


def _card(rtt, username):
    sig = "Excellent" if rtt < 250 else ("Good" if rtt < 600 else "Slow")
    return (
        f"{title('p o n g', '⚡')}\n\n"
        + quote(
            f"{kv('Latency', f'{rtt} ms')}\n"
            f"◈ <b>Signal</b>  :  <b>{sig}</b>\n"
            f"{kv('Uptime', _uptime())}\n"
            f"{kv('Bot', '@' + username)}"
        )
        + f"\n{footer()}"
    )


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=r"^[\.!/]ping(?: |$)"))
        async def ping(e):
            t0 = time.time()
            me = await e.client.get_me()
            rtt = round((time.time() - t0) * 1000, 2)
            await e.reply(_card(rtt, me.username or "bot"), parse_mode="html")

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
