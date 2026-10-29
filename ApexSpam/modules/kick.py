from telethon import events
from config import CMD_HNDLR, CLIENTS, OWNER_ID
from models.sudo import is_sudo

def register():
    pat = rf"\{CMD_HNDLR}kick(?: |$)"
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=pat))
        async def h(e):
            if e.sender_id != OWNER_ID and not await is_sudo(e.sender_id):
                return
            if not (e.is_group or e.is_channel):
                return await e.reply("Groups only.")
            uid = None
            if e.reply_to_msg_id:
                r = await e.get_reply_message()
                uid = r.sender_id
            else:
                parts = e.text.split(maxsplit=1)
                if len(parts) < 2:
                    return await e.reply(f"Usage: `{CMD_HNDLR}kick <user|reply>`", parse_mode="md")
                try:
                    ent = await e.client.get_entity(parts[1].strip())
                    uid = ent.id
                except Exception:
                    return await e.reply("❌ User not found.", parse_mode="md")
            try:
                await e.client.kick_participant(e.chat_id, uid)
                await e.reply(f"👢 Kicked `{uid}`", parse_mode="md")
            except Exception as err:
                await e.reply(f"❌ Failed: `{err}`", parse_mode="md")
