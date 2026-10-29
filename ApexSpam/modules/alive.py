import time
from telethon import events, Button
from ApexSpam import HNDLR, START_TIME, X1, X2, X3, X4, X5, X6, X7, X8, X9, X10
from ApexSpam.ui import header, kv

REPO_URL = "https://github.com/oyevipthoma88/Apex_spam_X"
CHANNEL_URL = "https://t.me/ApexSpamXSupport"


def _card(username: str) -> str:
    up = int(time.time() - START_TIME)
    h, r = divmod(up, 3600)
    m, s = divmod(r, 60)
    return (
        f"{header('apex alive', '💠')}\n\n"
        f"{kv('Bot', '@' + username)}\n"
        f"{kv('Prefix', HNDLR)}\n"
        f"{kv('Uptime', f'{h}h {m}m {s}s')}\n"
        f"{kv('Engine', 'Telethon')}\n"
        f"{kv('Database', 'MongoDB')}\n"
        f"{kv('Status', '✅ Online')}\n\n"
        "╭─〔 **SYSTEM** 〕─╮\n"
        "│  ◈  Clients healthy\n"
        "│  ◈  Handlers loaded\n"
        "│  ◈  24×7 ready\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
        "_Apex Spam X • always up._"
    )


def register():
    for c in [X1, X2, X3, X4, X5, X6, X7, X8, X9, X10]:
        @c.on(events.NewMessage(pattern=rf"\{HNDLR}alive(?: |$)"))
        async def alive(e):
            me = await e.client.get_me()
            buttons = [
                [Button.inline("📊 Stats", data="ax_stats")],
                [Button.url("📂 Repo", REPO_URL), Button.url("💬 Support", CHANNEL_URL)],
            ]
            await e.reply(_card(me.username or "bot"), buttons=buttons, parse_mode="md")

        @c.on(events.CallbackQuery(data=b"ax_stats"))
        async def ax_stats(e):
            up = int(time.time() - START_TIME)
            h, r = divmod(up, 3600)
            m, s = divmod(r, 60)
            text = (
                f"{header('apex stats', '📊')}\n\n"
                f"{kv('Uptime', f'{h}h {m}m {s}s')}\n"
                f"{kv('Clients', 'configurable')}\n"
                f"{kv('Prefix', HNDLR)}\n"
                f"{kv('Storage', 'MongoDB')}\n\n"
                "_Live metrics._"
            )
            await e.edit(text, buttons=[[Button.inline("« Back", data="ax_back")]], parse_mode="md")

        @c.on(events.CallbackQuery(data=b"ax_back"))
        async def ax_back(e):
            me = await e.client.get_me()
            buttons = [
                [Button.inline("📊 Stats", data="ax_stats")],
                [Button.url("📂 Repo", REPO_URL), Button.url("💬 Support", CHANNEL_URL)],
            ]
            await e.edit(_card(me.username or "bot"), buttons=buttons, parse_mode="md")
