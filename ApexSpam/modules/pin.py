from telethon import events
from config import CLIENTS, CMD_HNDLR
from ApexSpam.patterns import cmd
from ApexSpam.modules._helpers import has_perm

def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=cmd("pin")))
        async def pin(e):
            if not await has_perm(e):
                return
            if not e.reply_to_msg_id:
                return await e.reply("Reply to a message to pin.", parse_mode="md")
            try:
                await e.client.pin_message(e.chat_id, e.reply_to_msg_id, notify=False)
                await e.reply("📌 Pinned.")
            except Exception as err:
                await e.reply(f"❌ {err}")
