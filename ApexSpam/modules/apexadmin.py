import os
from telethon import events
from ApexSpam import (
    HNDLR, OWNER_ID, HEROKU_APP_NAME, HEROKU_API_KEY,
    X1, X2, X3, X4, X5, X6, X7, X8, X9, X10,
)
from ApexSpam.ui import header, kv


def register():
    for c in [X1, X2, X3, X4, X5, X6, X7, X8, X9, X10]:
        @c.on(events.NewMessage(pattern=rf"^[\.!/]axlogs(?: |$)"))
        async def axlogs(e):
            if e.sender_id != OWNER_ID:
                return
            if not HEROKU_APP_NAME or not HEROKU_API_KEY:
                return await e.reply(
                    f"{header('heroku logs', '⚠️')}\n\n"
                    f"{kv('Missing', 'HEROKU_APP_NAME / HEROKU_API_KEY')}",
                    parse_mode="md",
                )
            try:
                import heroku3
                h = heroku3.from_key(HEROKU_API_KEY)
                app = h.app(HEROKU_APP_NAME)
                text = app.get_log()
                path = "/tmp/apex_logs.txt"
                with open(path, "w") as f:
                    f.write(text)
                cap = (
                    f"{header('heroku logs', '📜')}\n\n"
                    f"{kv('App', HEROKU_APP_NAME)}\n"
                    f"{kv('Lines', len(text.splitlines()))}"
                )
                await e.client.send_file(e.chat_id, path, caption=cap, parse_mode="md")
                os.remove(path)
            except Exception as err:
                await e.reply(f"{header('heroku logs', '❌')}\n\n`{err}`", parse_mode="md")

        @c.on(events.NewMessage(pattern=rf"^[\.!/]axreboot(?: |$)"))
        async def axreboot(e):
            if e.sender_id != OWNER_ID:
                return
            if not HEROKU_APP_NAME or not HEROKU_API_KEY:
                return await e.reply(
                    f"{header('heroku restart', '⚠️')}\n\n"
                    f"{kv('Missing', 'HEROKU_APP_NAME / HEROKU_API_KEY')}",
                    parse_mode="md",
                )
            try:
                import heroku3
                h = heroku3.from_key(HEROKU_API_KEY)
                app = h.app(HEROKU_APP_NAME)
                await e.reply(
                    f"{header('restarting', '♻️')}\n\n"
                    f"{kv('App', HEROKU_APP_NAME)}\n\n"
                    "_Restarting via Heroku API..._",
                    parse_mode="md",
                )
                app.restart()
            except Exception as err:
                await e.reply(f"{header('restart', '❌')}\n\n`{err}`", parse_mode="md")
