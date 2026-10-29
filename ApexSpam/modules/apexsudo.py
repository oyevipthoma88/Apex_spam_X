from telethon import events
from ApexSpam import HNDLR, OWNER_ID, CLIENTS, SUDO_USERS
from ApexSpam.ui import header, kv
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
                return await e.reply(
                    f"{header('addsudo', '⚠️')}\n\n"
                    f"{kv('Usage', f'{HNDLR}addsudo <id|reply|@user>')}\n"
                    f"{kv('Perm', 'Owner')}",
                    parse_mode="md",
                )
            await add_sudo(uid, e.sender_id)
            await e.reply(
                f"{header('sudo added', '✅')}\n\n"
                f"{kv('User', uid)}\n"
                f"{kv('Store', 'MongoDB + Env')}\n"
                f"{kv('By', e.sender_id)}\n\n"
                "_Access granted._",
                parse_mode="md",
            )

        @c.on(events.NewMessage(pattern=rf"\{HNDLR}delsudo(?: |$)"))
        async def delsudo(e):
            if e.sender_id != OWNER_ID:
                return
            parts = e.text.split(maxsplit=1)
            uid = await _resolve(e, parts[1] if len(parts) > 1 else "")
            if not uid:
                return await e.reply(
                    f"{header('delsudo', '⚠️')}\n\n"
                    f"{kv('Usage', f'{HNDLR}delsudo <id|reply|@user>')}",
                    parse_mode="md",
                )
            ok = await remove_sudo(uid)
            emoji = "🗑️" if ok else "ℹ️"
            status = "Removed" if ok else "Not found"
            await e.reply(
                f"{header('sudo removed', emoji)}\n\n"
                f"{kv('User', uid)}\n"
                f"{kv('Status', status)}\n\n"
                "_Access revoked._" if ok else "_No change._",
                parse_mode="md",
            )

        @c.on(events.NewMessage(pattern=rf"\{HNDLR}listsudo(?: |$)"))
        async def listsudo(e):
            if e.sender_id != OWNER_ID:
                return
            ids = await mongo_ids()
            combined = sorted(set(ids) | set(SUDO_USERS))
            body = "\n".join(f"│  ◈ `{i}`" for i in combined) or "│  _none_"
            await e.reply(
                f"{header('sudo list', '🔐')}\n\n"
                f"╭─〔 **USERS ({len(combined)})** 〕─╮\n"
                f"{body}\n"
                "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
                "_Union of MongoDB + SUDO_USERS env._",
                parse_mode="md",
            )
