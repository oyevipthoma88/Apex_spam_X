"""Apex Spam X — ping + reboot (clean)."""
import time
from telethon import events
from ApexSpam import HNDLR, OWNER_ID, START_TIME, HEROKU_APP_NAME, HEROKU_API_KEY, CLIENTS
from ApexSpam.ui import header, kv


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=rf"\{HNDLR}ping(?: |$)"))
        async def ping(e):
            t0 = time.time()
            msg = await e.reply("⚡ `Pinging...`", parse_mode="md")
            lat = round((time.time() - t0) * 1000, 2)
            up = int(time.time() - START_TIME)
            h, r = divmod(up, 3600)
            m, s = divmod(r, 60)
            text = (
                f"{header('pong', '⚡')}\n\n"
                f"{kv('Latency', f'{lat} ms')}\n"
                f"{kv('Uptime', f'{h}h {m}m {s}s')}\n"
                f"{kv('Status', '✅ Online')}\n"
                f"{kv('Engine', 'Apex Spam X')}\n\n"
                "_Always up._"
            )
            await msg.edit(text, parse_mode="md")

        @c.on(events.NewMessage(pattern=rf"\{HNDLR}reboot(?: |$)"))
        async def reboot(e):
            if e.sender_id != OWNER_ID:
                return
            if not HEROKU_APP_NAME or not HEROKU_API_KEY:
                return await e.reply(
                    f"{header('reboot', '⚠️')}\n\n"
                    f"{kv('Missing', 'HEROKU_APP_NAME / HEROKU_API_KEY')}",
                    parse_mode="md",
                )
            try:
                import heroku3
                h = heroku3.from_key(HEROKU_API_KEY)
                app = h.app(HEROKU_APP_NAME)
                await e.reply(
                    f"{header('rebooting', '♻️')}\n\n"
                    f"{kv('App', HEROKU_APP_NAME)}\n\n"
                    "_Restarting via Heroku API..._",
                    parse_mode="md",
                )
                app.restart()
            except Exception as err:
                await e.reply(f"{header('reboot', '❌')}\n\n`{err}`", parse_mode="md")
