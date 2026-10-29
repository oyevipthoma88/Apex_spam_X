import asyncio
from telethon import events
from telethon.errors import FloodWaitError
from config import CMD_HNDLR, CLIENTS, OWNER_ID
from models.sudo import is_sudo

def register():
    pat = rf"\{CMD_HNDLR}emoji(?: |$)"
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=pat))
        async def h(e):
            if e.sender_id != OWNER_ID and not await is_sudo(e.sender_id):
                return
            parts = e.text.split(maxsplit=2)
            usage = f"Usage: `{CMD_HNDLR}emoji <emoji> <count>`"
            if len(parts) < 3:
                return await e.reply(usage, parse_mode="md")
            emoji = parts[1]
            try:
                cnt = int(parts[2])
            except ValueError:
                return await e.reply("❌ Count must be number.", parse_mode="md")
            if cnt < 1 or cnt > 100:
                return await e.reply("❌ Count 1–100.", parse_mode="md")
            for _ in range(cnt):
                try:
                    await e.client.send_message(e.chat_id, emoji)
                except FloodWaitError as fe:
                    await asyncio.sleep(fe.seconds)
                except Exception:
                    pass
                await asyncio.sleep(0.1)
