from telethon import events
from ApexSpam import HNDLR, OWNER_ID, CLIENTS
from ApexSpam.ui import header, quote, kv, divider
from ApexSpam.buttons import ib
from ApexSpam import roles
from models.sudo import add_sudo, remove_sudo, all_records


async def _resolve(event, arg):
    if arg and arg.lstrip("-").isdigit():
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
        @c.on(events.NewMessage(pattern=r"^[\.!/]addsudo(?: |$)"))
        async def addsudo(e):
            parts = e.text.split(maxsplit=1)
            uid = await _resolve(e, parts[1] if len(parts) > 1 else "")
            if not uid:
                return await e.reply(
                    f"{header('addsudo', '⚠️')}\n\n"
                    + quote(f"<code>{HNDLR}addsudo ID</code> / reply / @user"),
                    parse_mode="html",
                )
            ok, why = await roles.can_add_sudo(e.sender_id, uid)
            if not ok:
                return await e.reply(
                    f"{header('denied', '❌')}\n\n" + quote(why), parse_mode="html"
                )
            await add_sudo(uid, added_by=e.sender_id)
            roles.invalidate(uid)
            await e.reply(
                f"{header('sudo added', '✅')}\n\n"
                + quote(
                    f"{kv('User', uid)}\n{kv('Added by', e.sender_id)}\n{kv('Store', 'MongoDB')}",
                    expandable=True,
                ),
                parse_mode="html",
            )

        @c.on(events.NewMessage(pattern=r"^[\.!/]delsudo(?: |$)"))
        async def delsudo(e):
            parts = e.text.split(maxsplit=1)
            uid = await _resolve(e, parts[1] if len(parts) > 1 else "")
            if not uid:
                return await e.reply(
                    f"{header('delsudo', '⚠️')}\n\n"
                    + quote(f"<code>{HNDLR}delsudo ID</code> / reply / @user"),
                    parse_mode="html",
                )
            ok, why = await roles.can_del_sudo(e.sender_id, uid)
            if not ok:
                return await e.reply(
                    f"{header('denied', '❌')}\n\n" + quote(why), parse_mode="html"
                )
            ok2 = await remove_sudo(uid)
            roles.invalidate(uid)
            await e.reply(
                f"{header('sudo removed', '🗑️' if ok2 else 'ℹ️')}\n\n"
                + quote(f"{kv('User', uid)}\n{kv('Status', 'Removed' if ok2 else 'Not in DB')}",
                        expandable=True),
                parse_mode="html",
            )

        @c.on(events.NewMessage(pattern=r"^[\.!/]sudolist(?: |$)"))
        async def sudolist(e):
            r = await roles.role(e.sender_id)
            if r not in (roles.OWNER, roles.SUDO):
                return
            records = await all_records()
            if r != roles.OWNER:
                records = [x for x in records
                           if x.get("added_by") == e.sender_id or x["user_id"] == e.sender_id]
            rows = []
            for x in records:
                tag = x.get("source", "mongo")
                by = x.get("added_by", 0)
                by_label = "👑 owner" if by == OWNER_ID else f"👤 <code>{by}</code>"
                rows.append(f"◈ <code>{x['user_id']}</code>  <i>{tag}</i>  {by_label}")
            body = "\n".join(rows) or "<i>none</i>"
            await e.reply(
                f"{header('sudo list', '🔐')}\n\n"
                + quote(f"<b>Total</b> : <code>{len(records)}</code>")
                + f"\n\n{body}",
                parse_mode="html",
            )
