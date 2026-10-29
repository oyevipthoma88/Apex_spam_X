from telethon import events
from config import CMD_HNDLR, CLIENTS, OWNER_ID
from models.sudo import is_sudo

def register():
    pat = rf"\{CMD_HNDLR}echo(?: |$)"
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=pat))
        async def h(e):
            if e.sender_id != OWNER_ID and not await is_sudo(e.sender_id):
                return
            parts = e.text.split(maxsplit=1)
            if len(parts) < 2:
                return await e.reply(f"Usage: `{CMD_HNDLR}echo <text>`", parse_mode="md")
            await e.reply(parts[1])
