import os
import sys
from telethon import events
from config import CLIENTS, OWNER_ID
from ApexSpam.patterns import cmd


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=cmd("reboot"), incoming=True))
        async def reboot(e):
            if e.sender_id != OWNER_ID:
                return
            await e.reply("♻️ Rebooting...")
            for client in CLIENTS:
                try:
                    await client.disconnect()
                except Exception:
                    pass
            os.execl(sys.executable, sys.executable, *sys.argv)
