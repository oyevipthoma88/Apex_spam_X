from telethon import events
from config import CMD_HNDLR, CLIENTS, OWNER_ID
from models.sudo import is_sudo

def register():
    pat = rf"\{CMD_HNDLR}purge(?: |$)"
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=pat))
        async def h(e):
            if e.sender_id != OWNER_ID and not await is_sudo(e.sender_id):
                return
            if not e.reply_to_msg_id:
                return await e.reply("Reply to the message you want to start purging from.", parse_mode="md")
            ids = list(range(e.reply_to_msg_id, e.id + 1))
            deleted = 0
            for i in range(0, len(ids), 100):
                try:
                    await e.client.delete_messages(e.chat_id, ids[i:i+100])
                    deleted += len(ids[i:i+100])
                except Exception:
                    pass
            await e.reply(f"🧹 Purged ~{deleted} messages.", parse_mode="md")
