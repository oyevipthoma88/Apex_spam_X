from telethon import events
from config import HNDLR, OWNER_ID, CLIENTS, SUDO_USERS
from models.sudo import add_sudo, remove_sudo, mongo_ids


async def _resolve(event, arg):
    if arg and arg.isdigit():
        return int(arg)
    if event.reply_to_msg_id:
        r = await event.get_reply_message()
        return r.sender_id
    if arg:
        try:
            ent = await event.client.get_entity(arg)
            return ent.id
        except Exception:
            return None
    return None


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=rf"\{HNDLR}addsudo(?: |$)"))
        async def addsudo(e):
            if e.sender_id != OWNER_ID:
                return
            parts = e.text.split(maxsplit=1)
            uid = await _resolve(e, parts[1] if len(parts) > 1 else "")
            if not uid:
                return await e.reply(f"Usage: `{HNDLR}addsudo <id|reply|@user>`", parse_mode="md")
            await add_sudo(uid, e.sender_id)
            await e.reply(f"✅ `{uid}` added (Mongo + memory).", parse_mode="md")

        @c.on(events.NewMessage(pattern=rf"\{HNDLR}delsudo(?: |$)"))
        async def delsudo(e):
            if e.sender_id != OWNER_ID:
                return
            parts = e.text.split(maxsplit=1)
            uid = await _resolve(e, parts[1] if len(parts) > 1 else "")
            if not uid:
                return await e.reply(f"Usage: `{HNDLR}delsudo <id|reply|@user>`", parse_mode="md")
            ok = await remove_sudo(uid)
            await e.reply(f"🗑️ `{uid}` {'removed' if ok else 'not in DB'}.", parse_mode="md")

        @c.on(events.NewMessage(pattern=rf"\{HNDLR}listsudo(?: |$)"))
        async def listsudo(e):
            if e.sender_id != OWNER_ID:
                return
            ids = await mongo_ids()
            combined = sorted(set(ids) | set(SUDO_USERS))
            text = "**📋 Sudo Users:**\n" + "\n".join(f"• `{i}`" for i in combined)
            await e.reply(text, parse_mode="md")
