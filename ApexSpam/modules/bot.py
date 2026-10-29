"""Apex Spam X — premium ping + Heroku reboot."""
import time
from telethon import events
from ApexSpam import HNDLR, OWNER_ID, START_TIME, HEROKU_APP_NAME, HEROKU_API_KEY, CLIENTS
from ApexSpam.ui import header, quote, kv, divider, bar, footer

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
        return f"{round((time.time()-t)*1000, 2)} ms"
    except Exception:
        return "down"


def _uptime():
    up = int(time.time() - START_TIME)
    d, r = divmod(up, 86400)
    h, r = divmod(r, 3600)
    m, s = divmod(r, 60)
    return f"{d}d {h}h {m}m" if d else f"{h}h {m}m {s}s"


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=rf"\{HNDLR}ping(?: |$)"))
        async def ping(e):
            t0 = time.time()
            msg = await e.reply("⚡ <i>Measuring…</i>", parse_mode="html")
            rtt = round((time.time() - t0) * 1000, 2)
            t1 = time.time()
            await msg.edit("⚡ <i>Probing database…</i>", parse_mode="html")
            edit_lat = round((time.time() - t1) * 1000, 2)
            db = await _mongo_ms()
            status = "Excellent" if rtt < 250 else "Good" if rtt < 600 else "Slow"
            text = (
                f"{header('pong', '⚡')}\n\n"
                + quote(
                    f"<b>{bar(rtt)}</b>  <code>{rtt} ms</code>\n"
                    f"◈ <b>Signal</b>   :  <b>{status}</b>\n"
                    f"{kv('Round-trip', f'{rtt} ms')}\n"
                    f"{kv('Edit', f'{edit_lat} ms')}\n"
                    f"{kv('MongoDB', db)}",
                    expandable=True,
                )
                + "\n\n"
                + quote(f"{kv('Uptime', _uptime())}\n{kv('Clients', len(CLIENTS))}\n{kv('Status', '✅ Online')}", expandable=True)
                + f"\n\n{divider()}\n{footer()}"
            )
            await msg.edit(text, parse_mode="html")

        @c.on(events.NewMessage(pattern=rf"\{HNDLR}reboot(?: |$)"))
        async def reboot(e):
            if e.sender_id != OWNER_ID: return
            if not HEROKU_APP_NAME or not HEROKU_API_KEY:
                return await e.reply(
                    f"{header('reboot', '⚠️')}\n\n" + quote("Missing <code>HEROKU_APP_NAME</code> / <code>HEROKU_API_KEY</code>"),
                    parse_mode="html",
                )
            try:
                import heroku3
                app = heroku3.from_key(HEROKU_API_KEY).app(HEROKU_APP_NAME)
                await e.reply(
                    f"{header('rebooting', '♻️')}\n\n" + quote(f"{kv('App', HEROKU_APP_NAME)}\n\n<i>Heroku API restart…</i>"),
                    parse_mode="html",
                )
                app.restart()
            except Exception as err:
                await e.reply(f"{header('reboot', '❌')}\n\n" + quote(str(err)), parse_mode="html")
