"""Apex Spam X — spam (clean, no porn, sudo-gated)."""
import asyncio

from telethon import events
from telethon.errors import FloodWaitError

from ApexSpam import HNDLR, OWNER_ID, CLIENTS, SUDO_USERS
from ApexSpam.ui import header, quote, kv


def _is_authed(uid: int) -> bool:
    return uid == OWNER_ID or uid in SUDO_USERS


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=rf"\{HNDLR}spam(?: |$)"))
        async def spam(event):
            if not _is_authed(event.sender_id):
                return
            parts = event.text.split(maxsplit=2)
            if len(parts) < 2:
                return await event.reply(
                    f"{header('spam', '⚠️')}\n\n"
                    + quote(
                        f"<code>{HNDLR}spam COUNT TEXT</code>\n"
                        f"<code>{HNDLR}spam COUNT</code> (reply)",
                        expandable=True,
                    ),
                    parse_mode="html",
                )
            try:
                count = int(parts[1])
            except ValueError:
                return await event.reply(
                    f"{header('spam', '❌')}\n\n" + quote("Count must be a number."),
                    parse_mode="html",
                )
            if count < 1 or count > 200:
                return await event.reply(
                    f"{header('spam', '❌')}\n\n" + quote("Count must be 1–200."),
                    parse_mode="html",
                )

            reply = await event.get_reply_message() if event.reply_to_msg_id else None
            text_to_send = parts[2] if len(parts) >= 3 else (reply.text if reply and reply.text else None)
            if not text_to_send and not (reply and reply.media):
                return await event.reply(
                    f"{header('spam', '⚠️')}\n\n" + quote("Provide text or reply to a message."),
                    parse_mode="html",
                )

            sent = failed = 0
            for _ in range(count):
                try:
                    if reply and reply.media and len(parts) < 3:
                        await event.client.send_file(event.chat_id, reply, caption=reply.text or "")
                    else:
                        await event.client.send_message(event.chat_id, text_to_send or ".")
                    sent += 1
                except FloodWaitError as fe:
                    await asyncio.sleep(fe.seconds)
                except Exception:
                    failed += 1
                await asyncio.sleep(0.15)

            await event.reply(
                f"{header('spam done', '✅')}\n\n"
                + quote(
                    f"{kv('Sent', sent)}\n{kv('Failed', failed)}\n{kv('Total', count)}",
                    expandable=True,
                ),
                parse_mode="html",
            )
