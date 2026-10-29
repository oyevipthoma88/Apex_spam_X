from telethon import events
from telethon.tl.functions.channels import LeaveChannelRequest
from config import CLIENTS, OWNER_ID
from ApexSpam.patterns import cmd


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=cmd("leave"), incoming=True))
        async def leave(e):
            if e.sender_id != OWNER_ID:
                return
            if e.is_private:
                return await e.reply("Group me use karo ya chat id do.")
            try:
                await e.client(LeaveChannelRequest(e.chat_id))
                await e.reply("👋 Left the chat.")
            except Exception as err:
                await e.reply(f"❌ {err}")
