"""Apex Spam X — banall, unbanall, nc (title changer)."""
import asyncio

from telethon import events
from telethon.errors import FloodWaitError
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import (
    ChannelParticipantsAdmins,
    ChannelParticipantsKicked,
    ChatBannedRights,
)

from ApexSpam import HNDLR, OWNER_ID, CLIENTS, SUDO_USERS
from ApexSpam.ui import header, quote, kv, divider
from ApexSpam.buttons import ib

PENDING = {}


def _authed(uid):
    return uid == OWNER_ID or uid in SUDO_USERS


async def _admin_ok(client, chat):
    me = await client.get_me()
    try:
        perms = await client.get_permissions(chat, me.id)
        return bool(getattr(perms, "is_admin", False))
    except Exception:
        return False


def _confirm(title, emoji, lines, ok_label, ok_data, no_data):
    return (
        f"{header(title, emoji)}\n\n"
        + quote(lines, expandable=True)
        + f"\n\n{divider()}\n<i>This cannot be undone.</i>",
        [[ib(ok_label, ok_data, "danger"), ib("✖ Cancel", no_data, "success")]],
    )


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=rf"^[{HNDLR}!/]banall(?: |$)"))
        async def banall(e):
            if not _authed(e.sender_id): return
            if not (e.is_group or e.is_channel):
                return await e.reply("❌ Groups only.", parse_mode="html")
            if not await _admin_ok(e.client, e.chat_id):
                return await e.reply("❌ Bot needs admin + ban rights.", parse_mode="html")
            PENDING[(e.chat_id, e.sender_id)] = "banall"
            text, btns = _confirm(
                "ban all", "🔨",
                f"{kv('Chat', e.chat_id)}\n{kv('Target', 'all non-admin members')}",
                "🔨 Confirm banall", b"axmod_ok", b"axmod_no",
            )
            await e.reply(text, buttons=btns, parse_mode="html")

        @c.on(events.NewMessage(pattern=rf"^[{HNDLR}!/]unbanall(?: |$)"))
        async def unbanall(e):
            if not _authed(e.sender_id): return
            if not (e.is_group or e.is_channel):
                return await e.reply("❌ Groups only.", parse_mode="html")
            if not await _admin_ok(e.client, e.chat_id):
                return await e.reply("❌ Bot needs admin + ban rights.", parse_mode="html")
            PENDING[(e.chat_id, e.sender_id)] = "unbanall"
            text, btns = _confirm(
                "unban all", "♻️",
                f"{kv('Chat', e.chat_id)}\n{kv('Target', 'all banned users')}",
                "♻️ Confirm unbanall", b"axmod_ok", b"axmod_no",
            )
            await e.reply(text, buttons=btns, parse_mode="html")

        @c.on(events.NewMessage(pattern=rf"^[{HNDLR}!/]nc(?: |$)"))
        async def nc(e):
            if not _authed(e.sender_id): return
            if not (e.is_group or e.is_channel):
                return await e.reply("❌ Groups only.", parse_mode="html")
            if not await _admin_ok(e.client, e.chat_id):
                return await e.reply("❌ Bot needs admin rights.", parse_mode="html")
            parts = e.text.split(maxsplit=2)
            if len(parts) < 3:
                return await e.reply(
                    f"<b>Usage</b>\n<code>{HNDLR}nc COUNT TEXT</code>",
                    parse_mode="html",
                )
            try:
                count = int(parts[1])
            except ValueError:
                return await e.reply("❌ Count must be number.", parse_mode="html")
            count = max(1, min(count, 100))
            title = parts[2]
            changed = 0
            for _ in range(count):
                try:
                    await e.client.edit_title(e.chat_id, title)
                    changed += 1
                except FloodWaitError as fe:
                    await asyncio.sleep(fe.seconds + 2)
                except Exception:
                    pass
                await asyncio.sleep(0.4)
            await e.reply(
                f"<b>📝 Title changed ×{changed}</b>\n<code>{title}</code>",
                parse_mode="html",
            )

        @c.on(events.CallbackQuery(data=b"axmod_no"))
        async def cancel(e):
            PENDING.pop((e.chat_id, e.sender_id), None)
            await e.answer("Cancelled")
            await e.edit(
                f"{header('cancelled', '✖')}\n\n" + quote("No action taken."),
                parse_mode="html",
            )

        @c.on(events.CallbackQuery(data=b"axmod_ok"))
        async def confirm(e):
            if not _authed(e.sender_id):
                return await e.answer("Not allowed.", alert=True)
            job = PENDING.pop((e.chat_id, e.sender_id), None)
            if not job:
                return await e.answer("Expired.", alert=True)
            await e.answer("Running…")
            if job == "banall":
                await _do_banall(e)
            elif job == "unbanall":
                await _do_unbanall(e)


async def _progress(msg, title, done, total, emoji):
    try:
        await msg.edit(
            f"{header(title, emoji)}\n\n"
            + quote(f"{kv('Processed', done)}\n{kv('Done', total)}"),
            parse_mode="html",
        )
    except Exception:
        pass


async def _do_banall(e):
    client, chat = e.client, e.chat_id
    msg = await e.edit(f"{header('banall', '🔨')}\n\n" + quote("Collecting…"), parse_mode="html")
    me = await client.get_me()
    skip = {me.id, OWNER_ID, *SUDO_USERS}
    try:
        async for p in client.iter_participants(chat, filter=ChannelParticipantsAdmins):
            skip.add(p.id)
    except Exception:
        pass
    rights = ChatBannedRights(until_date=None, view_messages=True)
    banned = failed = seen = 0
    async for p in client.iter_participants(chat, aggressive=True):
        seen += 1
        if p.id in skip or getattr(p, "bot", False) or getattr(p, "deleted", False):
            continue
        try:
            await client(EditBannedRequest(chat, p.id, rights))
            banned += 1
        except FloodWaitError as fe:
            await asyncio.sleep(fe.seconds + 2)
        except Exception:
            failed += 1
        if seen % 15 == 0:
            await _progress(msg, "banall", banned + failed, seen, "🔨")
        await asyncio.sleep(0.05)
    await msg.edit(
        f"{header('banall done', '✅')}\n\n"
        + quote(f"{kv('Banned', banned)}\n{kv('Failed', failed)}", expandable=True),
        parse_mode="html",
    )


async def _do_unbanall(e):
    client, chat = e.client, e.chat_id
    msg = await e.edit(f"{header('unbanall', '♻️')}\n\n" + quote("Fetching…"), parse_mode="html")
    rights = ChatBannedRights(until_date=None)
    freed = failed = seen = 0
    async for p in client.iter_participants(chat, filter=ChannelParticipantsKicked, aggressive=True):
        seen += 1
        try:
            await client(EditBannedRequest(chat, p.id, rights))
            freed += 1
        except FloodWaitError as fe:
            await asyncio.sleep(fe.seconds + 2)
        except Exception:
            failed += 1
        if seen % 15 == 0:
            await _progress(msg, "unbanall", freed + failed, seen, "♻️")
        await asyncio.sleep(0.05)
    await msg.edit(
        f"{header('unbanall done', '✅')}\n\n"
        + quote(f"{kv('Unbanned', freed)}\n{kv('Failed', failed)}", expandable=True),
        parse_mode="html",
    )
