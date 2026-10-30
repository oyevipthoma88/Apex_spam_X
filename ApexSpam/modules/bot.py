"""Apex Spam X — compact ping + Heroku reboot."""
import time

from telethon import events

from ApexSpam import HNDLR, OWNER_ID, START_TIME, HEROKU_APP_NAME, HEROKU_API_KEY, CLIENTS
from ApexSpam.ui import quote, kv, footer, title

try:
    from database import mongo_client
except Exception:
    mongo_client = None


async def _mongo_ms():
    if mongo_client is None:
        return "n/a"
    t = time.time()
    try:
        await mongo_client.admin.command("ping")
        return f"{round((time.time() - t) * 1000, 2)} ms"
    except Exception:
        return "down"


def _uptime():
    up = int(time.time() - START_TIME)
    d, r = divmod(up, 86400)
    h, r = divmod(r, 3600)
    m, s = divmod(r, 60)
    return f"{d}d {h}h {m}m" if d else f"{h}h {m}m"


def _card(rtt, db):
    sig = "Excellent" if rtt < 250 else ("Good" if rtt < 600 else "Slow")
    return (
        f"{title('p o n g', '⚡')}\n"
        + quote(
            f"{kv('Latency', f'{rtt} ms')}\n"
            f"◈ <b>Signal</b>  :  <b>{sig}</b>\n"
            f"{kv('Uptime', _uptime())}\n"
            f"{kv('MongoDB', db)}"
        )
        + f"\n{footer()}"
    )


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=rf"\{HNDLR}ping(?: |$)"))
        async def ping(e):
            t0 = time.time()
            msg = await e.reply("⚡", parse_mode="html")
            rtt = round((time.time() - t0) * 1000, 2)
            db = await _mongo_ms()
            await msg.edit(_card(rtt, db), parse_mode="html")

        @c.on(events.NewMessage(pattern=rf"\{HNDLR}reboot(?: |$)"))
        async def reboot(e):
            if e.sender_id != OWNER_ID:
                return
            if not HEROKU_APP_NAME or not HEROKU_API_KEY:
                return await e.reply(
                    "⚠️ Missing <code>HEROKU_APP_NAME</code> / <code>HEROKU_API_KEY</code>",
                    parse_mode="html",
                )
            try:
                import heroku3
                app = heroku3.from_key(HEROKU_API_KEY).app(HEROKU_APP_NAME)
                await e.reply(f"♻️ Restarting <code>{HEROKU_APP_NAME}</code>…", parse_mode="html")
                app.restart()
            except Exception as err:
                await e.reply(f"❌ <code>{err}</code>", parse_mode="html")
