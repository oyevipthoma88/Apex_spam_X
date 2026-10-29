from telethon import events
from config import CLIENTS, CMD_HNDLR
from ApexSpam.patterns import cmd
from ApexSpam.modules._helpers import has_perm

def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=cmd("unpin")))
        async def unpin(e):
            if not await has_perm(e):
                return
            try:
                if e.reply_to_msg_id:
                    await e.client.unpin_message(e.chat_id, e.reply_to_msg_id)
                else:
                    await e.client.unpin_message(e.chat_id)
                await e.reply("📌 Unpinned.")
            except Exception as err:
                await e.reply(f"❌ {err}")
