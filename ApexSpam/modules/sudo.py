from telethon import events
from config import CMD_HNDLR, OWNER_ID, CLIENTS
from models.sudo import add_sudo, remove_sudo, is_sudo, all_sudo

async def _resolve_target(event, arg: str):
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
    add_pat = rf"\{CMD_HNDLR}addsudo(?: |$)"
    del_pat = rf"\{CMD_HNDLR}delsudo(?: |$)"
    list_pat = rf"\{CMD_HNDLR}listsudo(?: |$)"

    for client in CLIENTS:
        @client.on(events.NewMessage(pattern=add_pat))
        async def add_handler(event):
            if event.sender_id != OWNER_ID:
                return await event.reply("❌ Owner only.")
            parts = event.text.split(maxsplit=1)
            arg = parts[1].strip() if len(parts) > 1 else ""
            uid = await _resolve_target(event, arg)
            if not uid:
                return await event.reply(
                    f"Usage: `{CMD_HNDLR}addsudo <user_id | reply | @username>`",
                    parse_mode="md",
                )
            await add_sudo(uid, event.sender_id)
            await event.reply(f"✅ `{uid}` added to sudo.", parse_mode="md")

        @client.on(events.NewMessage(pattern=del_pat))
        async def del_handler(event):
            if event.sender_id != OWNER_ID:
                return await event.reply("❌ Owner only.")
            parts = event.text.split(maxsplit=1)
            arg = parts[1].strip() if len(parts) > 1 else ""
            uid = await _resolve_target(event, arg)
            if not uid:
                return await event.reply(
                    f"Usage: `{CMD_HNDLR}delsudo <user_id | reply | @username>`",
                    parse_mode="md",
                )
            ok = await remove_sudo(uid)
            msg = f"🗑️ `{uid}` removed from sudo." if ok else f"⚠️ `{uid}` not in sudo list."
            await event.reply(msg, parse_mode="md")

        @client.on(events.NewMessage(pattern=list_pat))
        async def list_handler(event):
            if event.sender_id != OWNER_ID and not await is_sudo(event.sender_id):
                return await event.reply("❌ Sudo/Owner only.")
            ids = await all_sudo()
            if not ids:
                return await event.reply("📋 No sudo users yet.")
            text = "**📋 Sudo Users:**\n" + "\n".join(f"• `{i}`" for i in ids)
            await event.reply(text, parse_mode="md")
