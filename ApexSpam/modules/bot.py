"""Apex Spam X — ping + reboot (premium HTML)."""
import time
from telethon import events
from ApexSpam import HNDLR, OWNER_ID, START_TIME, HEROKU_APP_NAME, HEROKU_API_KEY, CLIENTS
from ApexSpam.ui import header, quote, kv


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=rf"\{HNDLR}ping(?: |$)"))
        async def ping(e):
            t0 = time.time()
            msg = await e.reply("⚡ <i>Pinging...</i>", parse_mode="html")
            lat = round((time.time() - t0) * 1000, 2)
            up = int(time.time() - START_TIME)
            h, r = divmod(up, 3600)
            m, s = divmod(r, 60)
            text = (
                f"{header('pong', '⚡')}\n\n"
                + quote(
                    f"{kv('Latency', f'{lat} ms')}\n"
                    f"{kv('Uptime', f'{h}h {m}m {s}s')}\n"
                    f"{kv('Status', '✅ Online')}",
                    expandable=True,
                )
            )
            await msg.edit(text, parse_mode="html")

        @c.on(events.NewMessage(pattern=rf"\{HNDLR}reboot(?: |$)"))
        async def reboot(e):
            if e.sender_id != OWNER_ID:
                return
            if not HEROKU_APP_NAME or not HEROKU_API_KEY:
                return await e.reply(
                    f"{header('reboot', '⚠️')}\n\n" + quote("Missing <code>HEROKU_APP_NAME</code> / <code>HEROKU_API_KEY</code>"),
                    parse_mode="html",
                )
            try:
                import heroku3
                h = heroku3.from_key(HEROKU_API_KEY)
                app = h.app(HEROKU_APP_NAME)
                await e.reply(
                    f"{header('rebooting', '♻️')}\n\n" + quote(f"{kv('App', HEROKU_APP_NAME)}"),
                    parse_mode="html",
                )
                app.restart()
            except Exception as err:
                await e.reply(f"{header('reboot', '❌')}\n\n" + quote(str(err)), parse_mode="html")
