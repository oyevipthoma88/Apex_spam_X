"""Apex Spam X — reply-raid (.rraid / .drraid) + .stop."""
import asyncio
from random import choice

from telethon import events

from ApexSpam import HNDLR, CLIENTS
from ApexSpam import fonts, roles
from ApexSpam import data as D
from ApexSpam.raid_engine import _send, stop as stop_raid
from ApexSpam.ui import header, quote, kv

ACTIVE = {}
MAX_REPLY = 200
DELAY = 0.12


def _pack():
    return getattr(D, "REPLYRAID", None) or getattr(D, "RAID", []) or []


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=r"^[\.!/]rraid(?: |$)"))
        async def rraid(e):
            if not await roles.can_use(e.sender_id):
                return
            if not e.reply_to_msg_id:
                return await e.reply(
                    f"{header('rraid', '⚠️')}\n\n"
                    + quote(f"Reply to target with <code>{HNDLR}rraid COUNT</code>"),
                    parse_mode="html",
                )
            parts = e.text.split(maxsplit=1)
            if len(parts) < 2:
                return await e.reply(f"<code>{HNDLR}rraid COUNT</code>", parse_mode="html")
            try:
                count = int(parts[1])
            except ValueError:
                return await e.reply("❌ Count must be number.", parse_mode="html")
            count = max(1, min(count, MAX_REPLY))
            r = await e.get_reply_message()
            uid = r.sender_id
            if await roles.role(uid) != roles.USER:
                return await e.reply("❌ Protected user.", parse_mode="html")
            ACTIVE[(e.chat_id, uid)] = count
            await e.reply(
                f"{header('reply raid armed', '🎯')}\n\n"
                + quote(
                    f"{kv('Target', uid)}\n{kv('Charges', count)}\n"
                    f"{kv('Fire', 'on their next message')}",
                    expandable=True,
                ),
                parse_mode="html",
            )

        @c.on(events.NewMessage(pattern=r"^[\.!/]drraid(?: |$)"))
        async def drraid(e):
            if not await roles.can_use(e.sender_id):
                return
            keys = [k for k in ACTIVE if k[0] == e.chat_id]
            if not keys:
                return await e.reply("ℹ️ No reply-raid armed here.", parse_mode="html")
            for k in keys:
                ACTIVE.pop(k, None)
            await e.reply(f"🗑️ Reply-raid cleared ({len(keys)}).", parse_mode="html")

        @c.on(events.NewMessage(pattern=r"^[\.!/]stop(?: |$)"))
        async def stop(e):
            if not await roles.can_use(e.sender_id):
                return
            stop_raid(e.chat_id)
            cleared = [k for k in ACTIVE if k[0] == e.chat_id]
            for k in cleared:
                ACTIVE.pop(k, None)
            await e.reply("🛑 Aborted all raids in this chat.", parse_mode="html")

        @c.on(events.NewMessage())
        async def trigger(e):
            if e.out:
                return
            key = (e.chat_id, e.sender_id)
            n = ACTIVE.pop(key, None)
            if not n:
                return
            pack = _pack()
            if not pack:
                return
            try:
                name = e.sender.first_name or "User"
            except Exception:
                name = "User"
            mention = f"[{name}](tg://user?id={e.sender_id})"
            for _ in range(n):
                body = f"{mention} {fonts.fx(choice(pack))}"
                await _send(e.client, e.chat_id, body, is_private=e.is_private)
