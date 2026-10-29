from telethon import events
from ApexSpam import HNDLR, OWNER_ID, CLIENTS
from ApexSpam.ui import header, quote, kv


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=rf"\{HNDLR}gcdiag(?: |$)"))
        async def gcdiag(e):
            if e.sender_id != OWNER_ID:
                return
            if e.is_private:
                return await e.reply(
                    f"{header('gc diag', '⚠️')}\n\n" + quote("Run this inside a group."),
                    parse_mode="html",
                )
            try:
                me = await e.client.get_me()
                perms = await e.client.get_permissions(e.chat_id, me.id)
                is_admin = getattr(perms, "is_admin", False)
            except Exception as err:
                return await e.reply(f"{header('gc diag', '❌')}\n\n" + quote(str(err)), parse_mode="html")

            text = (
                f"{header('gc diag', '🩺')}\n\n"
                + quote(
                    f"{kv('Chat ID', e.chat_id)}\n"
                    f"{kv('Bot admin', 'YES' if is_admin else 'NO')}\n"
                    f"{kv('Privacy', 'must be OFF in BotFather')}",
                    expandable=True,
                )
                + "\n\n"
                + quote(
                    "Fix: BotFather → Group Privacy → <b>Turn Off</b>, "
                    "then <b>remove</b> bot from group and <b>re-add</b>."
                )
            )
            await e.reply(text, parse_mode="html")
