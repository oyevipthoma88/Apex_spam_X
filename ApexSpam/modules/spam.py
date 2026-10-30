"""Apex Spam X — spam (sudo-gated + log channel)."""
import asyncio

from telethon import events
from telethon.errors import FloodWaitError

from ApexSpam import HNDLR, OWNER_ID, CLIENTS
from ApexSpam import roles
from ApexSpam import sender as _sender
from ApexSpam import logger as xlog
from ApexSpam.fonts import fx
from ApexSpam.ui import bread, quote, kv, prog, pill, footer


async def _authed(uid):
    return await roles.can_use(uid)


async def _chat_title(e):
    if e.is_private:
        return "DM"
    try:
        return getattr(await e.get_chat(), "title", "unknown")
    except Exception:
        return "unknown"


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=rf"^[\.!/]spam(?: |$)"))
        async def spam(event):
            if not await _authed(event.sender_id):
                return
            parts = event.text.split(maxsplit=2)
            if len(parts) < 2:
                return await event.reply(
                    f"{header('spam', '⚠️')}\n\n"
                    + quote(
                        f"<code>{HNDLR}spam COUNT TEXT</code>\n"
                        f"<code>{HNDLR}spam COUNT</code> (reply)"
                    ),
                    parse_mode="html",
                )
            try:
                count = int(parts[1])
            except ValueError:
                return await event.reply("❌ Count must be a number.", parse_mode="html")
            if not 1 <= count <= 200:
                return await event.reply("❌ Count must be 1–200.", parse_mode="html")

            reply = await event.get_reply_message() if event.reply_to_msg_id else None
            txt = parts[2] if len(parts) >= 3 else (reply.text if reply and reply.text else None)
            if not txt and not (reply and reply.media):
                return await event.reply("❌ Provide text or reply to a message.", parse_mode="html")

            sent = failed = 0
            for _ in range(count):
                try:
                    if reply and reply.media and len(parts) < 3:
                        ok = await _sender.send_file(
                            event.client, event.chat_id, reply,
                            is_private=event.is_private,
                            caption=reply.text or "",
                        )
                    else:
                        ok = await _sender.send(
                            event.client, event.chat_id, fx(txt or "."),
                            is_private=event.is_private,
                        )
                    if ok:
                        sent += 1
                    else:
                        failed += 1
                except FloodWaitError as fe:
                    await asyncio.sleep(fe.seconds)
                except Exception:
                    failed += 1

            await event.reply(
                f"{bread('spam', 'done')}\n\n"
                + quote(
                    f"{pill('Completed', 'ok')}\n"
                    f"{prog(sent, sent + failed)}\n"
                    f"{kv('Sent', sent)}\n{kv('Failed', failed)}",
                    expandable=True,
                )
                + f"\n{footer()}",
                parse_mode="html",
            )

            try:
                await xlog.log_spam(
                    user_id=event.sender_id,
                    user_name=getattr(event.sender, "first_name", "User"),
                    chat_id=event.chat_id,
                    chat_title=await _chat_title(event),
                    count=sent,
                    preview=txt or "[media]",
                )
            except Exception:
                pass
