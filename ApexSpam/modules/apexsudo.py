from telethon import events
from ApexSpam import HNDLR, OWNER_ID, CLIENTS, SUDO_USERS
from ApexSpam.ui import header, quote, kv, divider
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
        @c.on(events.NewMessage(pattern=rf"^[\.!/]addsudo(?: |$)"))
        async def addsudo(e):
            if e.sender_id != OWNER_ID:
                return
            parts = e.text.split(maxsplit=1)
            uid = await _resolve(e, parts[1] if len(parts) > 1 else "")
            if not uid:
                return await e.reply(
                    f"{header('addsudo', '⚠️')}\n\n"
                    + quote(f"<b>Usage</b> : <code>{HNDLR}addsudo ID</code>\n"
                            f"<b>Or</b>    : reply to a user"),
                    parse_mode="html",
                )
            await add_sudo(uid, e.sender_id)
            await e.reply(
                f"{header('sudo added', '✅')}\n\n"
                + quote(
                    f"{kv('User', uid)}\n{kv('Store', 'MongoDB + Env')}\n{kv('By', e.sender_id)}",
                    expandable=True,
                ),
                parse_mode="html",
            )

        @c.on(events.NewMessage(pattern=rf"^[\.!/]delsudo(?: |$)"))
        async def delsudo(e):
            if e.sender_id != OWNER_ID:
                return
            parts = e.text.split(maxsplit=1)
            uid = await _resolve(e, parts[1] if len(parts) > 1 else "")
            if not uid:
                return await e.reply(
                    f"{header('delsudo', '⚠️')}\n\n"
                    + quote(f"<b>Usage</b> : <code>{HNDLR}delsudo ID</code>"),
                    parse_mode="html",
                )
            ok = await remove_sudo(uid)
            status = "Removed" if ok else "Not in DB"
            emoji = "🗑️" if ok else "ℹ️"
            await e.reply(
                f"{header('sudo removed', emoji)}\n\n"
                + quote(f"{kv('User', uid)}\n{kv('Status', status)}", expandable=True)
                + f"\n\n{divider()}\n<i>{'Access revoked.' if ok else 'No change.'}</i>",
                parse_mode="html",
            )

        @c.on(events.NewMessage(pattern=rf"^[\.!/]listsudo(?: |$)"))
        async def listsudo(e):
            if e.sender_id != OWNER_ID:
                return
            ids = await mongo_ids()
            combined = sorted(set(ids) | set(SUDO_USERS))
            body = "\n".join(f"  ◈ <code>{i}</code>" for i in combined) or "  <i>none</i>"
            await e.reply(
                f"{header('sudo list', '🔐')}\n\n"
                + quote(f"<b>Total</b>  :  <code>{len(combined)}</code>")
                + f"\n\n{body}",
                parse_mode="html",
            )
