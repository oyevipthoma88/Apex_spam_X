from telethon import events

from ApexSpam import HNDLR, OWNER_ID, CLIENTS
from ApexSpam import roles, respond
from ApexSpam.ui import bread, quote, kv, table, pill, footer, join_rows
from ApexSpam.buttons import ib, copy_btn
from models.sudo import add_sudo, remove_sudo, all_records


async def _resolve(e, arg):
    if arg and arg.lstrip("-").isdigit():
        return int(arg)
    if e.reply_to_msg_id:
        r = await e.get_reply_message()
        return r.sender_id
    if arg:
        try:
            ent = await e.client.get_entity(arg)
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
                    f"{bread('sudo', 'add')}\n\n"
                    + quote(f"<code>{HNDLR}addsudo ID</code> / reply / @user"),
                    parse_mode="html",
                )
            ok, why = await roles.can_add_sudo(e.sender_id, uid)
            if not ok:
                return await e.reply(f"{bread('sudo', 'add')}\n\n" + quote(f"❌ {why}"),
                                     parse_mode="html")
            await add_sudo(uid, added_by=e.sender_id)
            roles.invalidate(uid)

            dm_ok = False
            try:
                await e.client.send_message(
                    uid,
                    f"🎓 <b>Welcome to Apex Spam X sudo</b>\n\n"
                    f"Commands: <code>{HNDLR}help</code>\n"
                    f"Raid: <code>{HNDLR}raid 5 @user</code>\n"
                    f"Stop: <code>{HNDLR}stop</code>\n"
                    f"Custom: <code>{HNDLR}setcmd name response</code>",
                    parse_mode="html",
                )
                dm_ok = True
            except Exception:
                pass

            await e.reply(
                f"{bread('sudo', 'added')}\n\n"
                + quote(
                    f"{pill('Added', 'ok')}\n"
                    f"{kv('User', uid)}\n"
                    f"{kv('By', e.sender_id)}\n"
                    f"{kv('Tutorial DM', 'sent' if dm_ok else 'failed (user must /start first)')}",
                    expandable=True,
                )
                + f"\n{footer()}",
                parse_mode="html",
            )

        @c.on(events.NewMessage(pattern=r"^[\.!/]delsudo(?: |$)"))
        async def delsudo(e):
            parts = e.text.split(maxsplit=1)
            uid = await _resolve(e, parts[1] if len(parts) > 1 else "")
            if not uid:
                return await e.reply(f"<code>{HNDLR}delsudo ID</code>", parse_mode="html")
            ok, why = await roles.can_del_sudo(e.sender_id, uid)
            if not ok:
                return await e.reply(f"{bread('sudo', 'remove')}\n\n" + quote(f"❌ {why}"),
                                     parse_mode="html")
            gone = await remove_sudo(uid)
            roles.invalidate(uid)
            await e.reply(
                f"{bread('sudo', 'removed')}\n\n"
                + quote(f"{pill('Removed' if gone else 'Not found', 'ok' if gone else 'warn')}\n"
                        f"{kv('User', uid)}", expandable=True),
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
                by = x.get("added_by", 0)
                rows.append([
                    x["user_id"],
                    "owner" if by == OWNER_ID else by,
                    x.get("source", "mongo"),
                ])
            body = table(["USER", "BY", "SRC"], rows) if rows else "<i>none</i>"
            ids = "\n".join(str(x["user_id"]) for x in records[:20])
            btns = []
            cb = copy_btn("📋 Copy IDs", ids) if ids else None
            if cb:
                btns.append([cb])
            btns.append([ib("✖ Close", b"close", "danger")])
            await e.reply(
                f"{bread('sudo', 'list')}\n\n"
                + quote(f"{pill(f'{len(records)} users', 'info')}", expandable=True)
                + f"\n{body}",
                buttons=join_rows(btns),
                parse_mode="html",
            )
