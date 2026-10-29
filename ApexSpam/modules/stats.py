import time
from telethon import events
from config import START_TIME, CLIENTS, OWNER_ID, CMD_HNDLR
from ApexSpam.patterns import cmd
from models.sudo import all_sudo

def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=cmd("stats")))
        async def stats(e):
            if e.sender_id != OWNER_ID:
                return
            up = int(time.time() - START_TIME)
            sudos = await all_sudo()
            text = (
                "**📊 Apex Spam X — Stats**\n\n"
                f"**⏱️ Uptime:** `{up} sec`\n"
                f"**🤖 Clients:** `{len(CLIENTS)}`\n"
                f"**🛡️ Sudo Users:** `{len(sudos)}`\n"
                f"**📌 Prefix:** `{CMD_HNDLR}`\n"
            )
            await e.reply(text, parse_mode="md")
