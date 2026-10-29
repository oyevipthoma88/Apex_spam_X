import asyncio
from telethon import events
from telethon.errors import FloodWaitError
from config import CMD_HNDLR, CLIENTS, OWNER_ID
from models.sudo import is_sudo

def register():
    pat = rf"\{CMD_HNDLR}spam(?: |$)"
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=pat))
        async def h(e):
            if e.sender_id != OWNER_ID and not await is_sudo(e.sender_id):
                return
            parts = e.text.split(maxsplit=2)
            usage = f"**Usage:**\n`{CMD_HNDLR}spam <count> <text|reply>`"
            if len(parts) < 2:
                return await e.reply(usage, parse_mode="md")
            try:
                cnt = int(parts[1])
            except ValueError:
                return await e.reply("❌ Count must be number.", parse_mode="md")
            if cnt < 1 or cnt > 200:
                return await e.reply("❌ Count must be 1–200.", parse_mode="md")
            if len(parts) >= 3:
                text = parts[2]
            elif e.reply_to_msg_id:
                r = await e.get_reply_message()
                text = r.text or "."
            else:
                return await e.reply(usage, parse_mode="md")
            for _ in range(cnt):
                try:
                    await e.client.send_message(e.chat_id, text)
                except FloodWaitError as fe:
                    await asyncio.sleep(fe.seconds)
                except Exception:
                    pass
                await asyncio.sleep(0.15)
