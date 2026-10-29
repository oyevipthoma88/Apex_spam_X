import asyncio
from telethon import events
from config import CMD_HNDLR, CLIENTS, OWNER_ID
from models.sudo import is_sudo

def register():
    pat = rf"\{CMD_HNDLR}tagall(?: |$)"
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=pat))
        async def h(e):
            if e.sender_id != OWNER_ID and not await is_sudo(e.sender_id):
                return
            if not (e.is_group or e.is_channel):
                return await e.reply("Groups only.")
            parts = e.text.split(maxsplit=1)
            msg = parts[1] if len(parts) > 1 else "📢 Attention!"
            users = []
            try:
                async for m in e.client.iter_participants(e.chat_id):
                    if not m.bot and not m.deleted:
                        users.append(f"[{m.first_name or 'User'}](tg://user?id={m.id})")
            except Exception:
                return await e.reply("❌ Cannot fetch members.")
            for i in range(0, len(users), 5):
                chunk = " ".join(users[i:i+5])
                try:
                    await e.client.send_message(e.chat_id, f"{msg}\n{chunk}")
                except Exception:
                    pass
                await asyncio.sleep(1.2)
