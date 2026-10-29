from telethon import events
from config import CLIENTS
from ApexSpam.patterns import cmd

def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=cmd("id")))
        async def id_cmd(e):
            if e.reply_to_msg_id:
                r = await e.get_reply_message()
                await e.reply(f"**👤 User ID:** `{r.sender_id}`\n**💬 Chat ID:** `{e.chat_id}`", parse_mode="md")
            else:
                await e.reply(f"**👤 Your ID:** `{e.sender_id}`\n**💬 Chat ID:** `{e.chat_id}`", parse_mode="md")
