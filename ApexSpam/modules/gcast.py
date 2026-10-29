import asyncio
from telethon import events
from telethon.errors import FloodWaitError
from config import CMD_HNDLR, CLIENTS, OWNER_ID
from models.sudo import is_sudo

def register():
    pat = rf"\{CMD_HNDLR}gcast(?: |$)"
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=pat))
        async def h(e):
            if e.sender_id != OWNER_ID and not await is_sudo(e.sender_id):
                return
            parts = e.text.split(maxsplit=1)
            if len(parts) < 2:
                return await e.reply(f"Usage: `{CMD_HNDLR}gcast <text>`", parse_mode="md")
            text = parts[1]
            sent = failed = 0
            async for dialog in e.client.iter_dialogs():
                if not (dialog.is_group or dialog.is_channel):
                    continue
                try:
                    await e.client.send_message(dialog.id, text)
                    sent += 1
                except FloodWaitError as fe:
                    await asyncio.sleep(fe.seconds)
                except Exception:
                    failed += 1
                await asyncio.sleep(1.0)
            await e.reply(f"📢 Sent: `{sent}` | Failed: `{failed}`", parse_mode="md")
