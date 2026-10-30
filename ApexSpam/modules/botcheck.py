"""Apex Spam X — .botcheck: per-bot delivery status in current chat."""
import logging

from telethon import events

from ApexSpam import HNDLR, OWNER_ID, CLIENTS
from ApexSpam.ui import header, quote, table, footer

log = logging.getLogger("ApexSpam.botcheck")


async def _row(client, chat_id, is_private):
    try:
        me = await client.get_me()
        uname = me.username or "?"
        my_id = me.id
    except Exception:
        return ("?", "ERR", "❌")
    if is_private:
        return (f"@{uname}", "DM", "✅")
    try:
        perms = await client.get_permissions(chat_id, my_id)
        admin = bool(getattr(perms, "is_admin", False))
    except Exception:
        admin = None
    if admin is True:
        return (f"@{uname}", "admin", "✅ all")
    if admin is False:
        return (f"@{uname}", "member", "⚠️ privacy")
    return (f"@{uname}", "?", "❓")


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=r"^[\.!/]botcheck(?: |$)"))
        async def botcheck(e):
            if e.sender_id != OWNER_ID:
                return
            try:
                rows = []
                for cli in CLIENTS:
                    rows.append(await _row(cli, e.chat_id, e.is_private))
                body = table(["BOT", "ROLE", "RECEIVES"], rows)
                hint = ""
                if not e.is_private:
                    hint = (
                        "\n\n<blockquote>⚠️ <b>Privacy mode</b>\n"
                        "Non-admin bots with privacy ON receive only <code>/commands</code>.\n"
                        "Fix: make every bot <b>admin</b>, <i>or</i> BotFather → "
                        "/setprivacy → Disable → remove &amp; re-add the bot.</blockquote>"
                    )
                await e.reply(
                    f"{header('bot check', '🩺')}\n\n{body}{hint}\n{footer()}",
                    parse_mode="html",
                )
            except Exception as ex:
                log.exception(f"botcheck: {ex}")
