"""Apex Spam X — GC setup diagnostic."""
from telethon import events
from ApexSpam import HNDLR, OWNER_ID, CLIENTS
from ApexSpam.ui import bread, quote, kv, pill, footer
from ApexSpam.buttons import ib


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=r"^[\.!/]gcsetup(?: |$)"))
        async def gcsetup(e):
            if not (e.is_group or e.is_channel):
                return await e.reply("❌ Groups only.", parse_mode="html")
            if e.sender_id != OWNER_ID:
                return
            try:
                me = await e.client.get_me()
                perms = await e.client.get_permissions(e.chat_id, me.id)
                is_admin = bool(getattr(perms, "is_admin", False))
                can_send = True
            except Exception:
                is_admin, can_send = False, False

            status = (
                f"{pill('Bot admin', 'ok' if is_admin else 'bad')}\n"
                f"{kv('Chat ID', e.chat_id)}\n"
                f"{kv('Can send', 'YES' if can_send else 'NO')}"
            )
            if is_admin:
                hint = "<i>✅ Bot is admin — all commands will work.</i>"
            else:
                hint = (
                    "<b>⚠️ Bot is NOT admin</b>\n\n"
                    "If bot doesn't respond to <code>.ping</code>:\n\n"
                    "<b>Fix 1 (recommended)</b>\n"
                    "→ Make bot <b>admin</b> in this group.\n"
                    "Admins always receive every message.\n\n"
                    "<b>Fix 2</b>\n"
                    "→ @BotFather → <b>/setprivacy</b> → bot → <b>Disable</b>\n"
                    "→ <b>Remove bot</b> from group\n"
                    "→ <b>Re-add bot</b> (required — Telegram caches the setting at join time)\n\n"
                    "Then test <code>.ping</code> again."
                )
            text = (
                f"{bread('setup', 'gc')}\n\n"
                + quote(status, expandable=True)
                + "\n\n"
                + quote(hint, expandable=True)
                + f"\n{footer()}"
            )
            await e.reply(
                text,
                buttons=[[ib("✖ Close", b"close", "danger")]],
                parse_mode="html",
            )

        @c.on(events.CallbackQuery(data=b"close"))
        async def close(e):
            try:
                await e.delete()
            except Exception:
                pass
