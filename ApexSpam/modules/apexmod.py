"""Apex Spam X — banall, unbanall, nc (title changer + emoji variants)."""
import asyncio
import logging
import random

from telethon import events
from telethon.errors import (
    ChatAdminRequiredError,
    ChatNotModifiedError,
    FloodWaitError,
)
from telethon.tl.functions.channels import EditBannedRequest, EditTitleRequest
from telethon.tl.types import (
    ChannelParticipantsAdmins,
    ChannelParticipantsKicked,
    ChatBannedRights,
)

from ApexSpam import HNDLR, OWNER_ID, CLIENTS, SUDO_USERS
from ApexSpam.ui import header, quote, kv, divider
from ApexSpam.buttons import ib

log = logging.getLogger("ApexSpam.apexmod")
PENDING = {}

BAN_DELAY = 0.02
NC_DELAY = 1.0
PROGRESS_EVERY = 25

NC_EMOJIS = [
    "❤️", "🤪", "🔥", "💀", "⚡", "😈", "👑", "💯",
    "🎯", "🚀", "🥶", "🤡", "🖤", "💖", "🌟", "😎",
]


def _authed(uid):
    return uid == OWNER_ID or uid in SUDO_USERS


async def _admin_ok(client, chat, need="ban"):
    try:
        me = await client.get_me()
        perms = await client.get_permissions(chat, me.id)
        if not getattr(perms, "is_admin", False):
            return False, "Bot is not admin in this chat."
        if need == "ban" and not getattr(perms, "ban_users", False):
            return False, "Bot missing 'Ban Users' permission."
        if need == "title" and not getattr(perms, "change_info", False):
            return False, "Bot missing 'Change Group Info' permission."
        return True, ""
    except Exception as ex:
        return False, f"Permission check failed: {ex}"


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
            ok, why = await _admin_ok(e.client, e.chat_id, need="ban")
            if not ok: return await e.reply(f"❌ {why}", parse_mode="html")
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
            ok, why = await _admin_ok(e.client, e.chat_id, need="ban")
            if not ok: return await e.reply(f"❌ {why}", parse_mode="html")
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
            ok, why = await _admin_ok(e.client, e.chat_id, need="title")
            if not ok: return await e.reply(f"❌ {why}", parse_mode="html")

            parts = e.text.split(maxsplit=2)
            if len(parts) < 3:
                return await e.reply(
                    f"<b>Usage</b>\n<code>{HNDLR}nc COUNT TEXT</code>\n"
                    f"<i>Example:</i> <code>{HNDLR}nc 4 apex op</code>",
                    parse_mode="html",
                )
            try:
                count = int(parts[1])
            except ValueError:
                return await e.reply("❌ Count must be number.", parse_mode="html")
            count = max(1, min(count, 30))
            base = parts[2].strip()[:55] or "Apex"

            status = await e.reply(f"📝 Changing title ×{count}…")
            changed = errors = 0
            used_emoji = []

            for i in range(count):
                # Pick unique emoji per iteration
                remaining = [em for em in NC_EMOJIS if em not in used_emoji]
                if not remaining:
                    remaining = NC_EMOJIS
                emoji = random.choice(remaining)
                used_emoji.append(emoji)

                title = f"{emoji} {base} {emoji}"[:128]
                try:
                    await e.client(EditTitleRequest(channel=e.chat_id, title=title))
                    changed += 1
                    log.info(f"nc: {i+1}/{count} -> {emoji} {base} {emoji}")
                except ChatNotModifiedError:
                    # try different emoji
                    try:
                        alt = random.choice(NC_EMOJIS)
                        await e.client(EditTitleRequest(
                            channel=e.chat_id, title=f"{alt} {base} {alt}"[:128]))
                        changed += 1
                    except Exception:
                        errors += 1
                except ChatAdminRequiredError:
                    return await status.edit("❌ Bot lost Change Info permission.")
                except FloodWaitError as fe:
                    await asyncio.sleep(fe.seconds + 2)
                    errors += 1
                except Exception as ex:
                    log.exception(f"nc iter {i}: {ex}")
                    errors += 1
                await asyncio.sleep(NC_DELAY)

            try:
                await status.edit(
                    f"<b>📝 Title changed ×{changed}</b>\n"
                    f"<i>errors: {errors}</i>",
                    parse_mode="html",
                )
            except Exception:
                pass

        @c.on(events.CallbackQuery(data=b"axmod_no"))
        async def cancel(e):
            PENDING.pop((e.chat_id, e.sender_id), None)
            await e.answer("Cancelled")
            try:
                await e.edit(f"{header('cancelled', '✖')}\n\n" + quote("No action taken."),
                             parse_mode="html")
            except Exception:
                pass

        @c.on(events.CallbackQuery(data=b"axmod_ok"))
        async def confirm(e):
            if not _authed(e.sender_id):
                return await e.answer("Not allowed.", alert=True)
            job = PENDING.pop((e.chat_id, e.sender_id), None)
            if not job:
                return await e.answer("Expired.", alert=True)
            await e.answer("Running…")
            try:
                if job == "banall":
                    await _do_banall(e)
                elif job == "unbanall":
                    await _do_unbanall(e)
            except Exception as ex:
                log.exception(f"confirm {job}: {ex}")


async def _progress(msg, title, done, total, emoji):
    try:
        await msg.edit(
            f"{header(title, emoji)}\n\n"
            + quote(f"{kv('Processed', done)}\n{kv('Done', total)}", expandable=True),
            parse_mode="html",
        )
    except Exception:
        pass


async def _do_banall(e):
    client, chat = e.client, e.chat_id
    msg = await e.edit(f"{header('banall', '🔨')}\n\n" + quote("Collecting…"),
                       parse_mode="html")
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
            await asyncio.sleep(fe.seconds + 1)
        except Exception:
            failed += 1
        if seen % PROGRESS_EVERY == 0:
            await _progress(msg, "banall", banned + failed, seen, "🔨")
        await asyncio.sleep(BAN_DELAY)
    await msg.edit(
        f"{header('banall done', '✅')}\n\n"
        + quote(f"{kv('Banned', banned)}\n{kv('Failed', failed)}\n{kv('Scanned', seen)}",
                expandable=True),
        parse_mode="html",
    )


async def _do_unbanall(e):
    client, chat = e.client, e.chat_id
    msg = await e.edit(f"{header('unbanall', '♻️')}\n\n" + quote("Fetching…"),
                       parse_mode="html")
    rights = ChatBannedRights(until_date=None)
    freed = failed = seen = 0
    async for p in client.iter_participants(
        chat, filter=ChannelParticipantsKicked, aggressive=True
    ):
        seen += 1
        try:
            await client(EditBannedRequest(chat, p.id, rights))
            freed += 1
        except Exception:
            failed += 1
        if seen % PROGRESS_EVERY == 0:
            await _progress(msg, "unbanall", freed + failed, seen, "♻️")
        await asyncio.sleep(BAN_DELAY)
    await msg.edit(
        f"{header('unbanall done', '✅')}\n\n"
        + quote(f"{kv('Unbanned', freed)}\n{kv('Failed', failed)}", expandable=True),
        parse_mode="html",
    )
