"""Apex Spam X — banall, unbanall, nc (title changer, fast + error-safe)."""
import asyncio
import logging

from telethon import events
from telethon.errors import (
    ChatAdminRequiredError,
    ChatNotModifiedError,
    FloodWaitError,
)
from telethon.tl.functions.channels import EditBannedRequest
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

BAN_DELAY = 0.02       # banall per-ban gap
NC_DELAY = 1.0         # title change gap (Telegram rate limit)
PROGRESS_EVERY = 25


def _authed(uid):
    return uid == OWNER_ID or uid in SUDO_USERS


async def _admin_ok(client, chat, need="ban"):
    """Return (ok, reason). need='ban' or 'title'."""
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
        # ─── banall ───
        @c.on(events.NewMessage(pattern=rf"^[{HNDLR}!/]banall(?: |$)"))
        async def banall(e):
            if not _authed(e.sender_id):
                return
            if not (e.is_group or e.is_channel):
                return await e.reply("❌ Groups only.", parse_mode="html")
            ok, why = await _admin_ok(e.client, e.chat_id, need="ban")
            if not ok:
                return await e.reply(f"❌ {why}", parse_mode="html")
            PENDING[(e.chat_id, e.sender_id)] = "banall"
            text, btns = _confirm(
                "ban all", "🔨",
                f"{kv('Chat', e.chat_id)}\n{kv('Target', 'all non-admin members')}",
                "🔨 Confirm banall", b"axmod_ok", b"axmod_no",
            )
            await e.reply(text, buttons=btns, parse_mode="html")

        # ─── unbanall ───
        @c.on(events.NewMessage(pattern=rf"^[{HNDLR}!/]unbanall(?: |$)"))
        async def unbanall(e):
            if not _authed(e.sender_id):
                return
            if not (e.is_group or e.is_channel):
                return await e.reply("❌ Groups only.", parse_mode="html")
            ok, why = await _admin_ok(e.client, e.chat_id, need="ban")
            if not ok:
                return await e.reply(f"❌ {why}", parse_mode="html")
            PENDING[(e.chat_id, e.sender_id)] = "unbanall"
            text, btns = _confirm(
                "unban all", "♻️",
                f"{kv('Chat', e.chat_id)}\n{kv('Target', 'all banned users')}",
                "♻️ Confirm unbanall", b"axmod_ok", b"axmod_no",
            )
            await e.reply(text, buttons=btns, parse_mode="html")

        # ─── nc (title changer) ───
        @c.on(events.NewMessage(pattern=rf"^[{HNDLR}!/]nc(?: |$)"))
        async def nc(e):
            if not _authed(e.sender_id):
                return
            if not (e.is_group or e.is_channel):
                return await e.reply("❌ Groups only.", parse_mode="html")
            ok, why = await _admin_ok(e.client, e.chat_id, need="title")
            if not ok:
                return await e.reply(f"❌ {why}", parse_mode="html")

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
            count = max(1, min(count, 50))
            base = parts[2].strip()[:60] or "Apex"

            status = await e.reply(f"📝 Changing title ×{count}…")
            changed = errors = 0
            for i in range(count):
                # zero-width space makes each title unique — avoids ChatNotModifiedError
                title = base + ("\u200b" * (i + 1))
                try:
                    await e.client.edit_title(e.chat_id, title)
                    changed += 1
                    log.info(f"nc: title {i+1}/{count} → {base!r}")
                except ChatNotModifiedError:
                    # still try different suffix
                    try:
                        await e.client.edit_title(e.chat_id, base + "\u200b" * (i + 2))
                        changed += 1
                    except Exception as ex:
                        errors += 1
                        log.warning(f"nc not-modified fallback: {ex}")
                except ChatAdminRequiredError:
                    return await status.edit(
                        "❌ Bot lost admin / Change Info permission mid-way."
                    )
                except FloodWaitError as fe:
                    wait = fe.seconds + 2
                    log.warning(f"nc flood wait {wait}s")
                    await asyncio.sleep(wait)
                    try:
                        await e.client.edit_title(e.chat_id, base + "\u200b" * (i + 2))
                        changed += 1
                    except Exception:
                        errors += 1
                except Exception as ex:
                    log.exception(f"nc error iter {i}: {ex}")
                    errors += 1
                await asyncio.sleep(NC_DELAY)

            try:
                await status.edit(
                    f"<b>📝 Title changed ×{changed}</b>\n"
                    f"<code>{base}</code>\n"
                    f"<i>errors: {errors}</i>",
                    parse_mode="html",
                )
            except Exception:
                pass

        # ─── confirm / cancel ───
        @c.on(events.CallbackQuery(data=b"axmod_no"))
        async def cancel(e):
            PENDING.pop((e.chat_id, e.sender_id), None)
            await e.answer("Cancelled")
            try:
                await e.edit(
                    f"{header('cancelled', '✖')}\n\n" + quote("No action taken."),
                    parse_mode="html",
                )
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
                try:
                    await e.reply(f"❌ <code>{ex}</code>", parse_mode="html")
                except Exception:
                    pass


async def _progress(msg, title, done, total, emoji):
    try:
        await msg.edit(
            f"{header(title, emoji)}\n\n"
            + quote(f"{kv('Processed', done)}\n{kv('Done', total)}\n{kv('Status', 'running…')}"),
            parse_mode="html",
        )
    except Exception:
        pass


async def _do_banall(e):
    client, chat = e.client, e.chat_id
    msg = await e.edit(
        f"{header('banall', '🔨')}\n\n" + quote("Collecting members…"),
        parse_mode="html",
    )
    me = await client.get_me()
    skip = {me.id, OWNER_ID, *SUDO_USERS}
    try:
        async for p in client.iter_participants(chat, filter=ChannelParticipantsAdmins):
            skip.add(p.id)
    except Exception as ex:
        log.warning(f"admin fetch: {ex}")

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
            wait = fe.seconds + 1
            log.warning(f"banall flood {wait}s")
            await asyncio.sleep(wait)
            try:
                await client(EditBannedRequest(chat, p.id, rights))
                banned += 1
            except Exception:
                failed += 1
        except ChatAdminRequiredError:
            return await msg.edit(
                f"{header('banall', '❌')}\n\n"
                + quote("Bot lost ban permission. Aborted."),
                parse_mode="html",
            )
        except Exception as ex:
            log.debug(f"banall skip {p.id}: {ex}")
            failed += 1
        if seen % PROGRESS_EVERY == 0:
            await _progress(msg, "banall", banned + failed, seen, "🔨")
        await asyncio.sleep(BAN_DELAY)

    await msg.edit(
        f"{header('banall done', '✅')}\n\n"
        + quote(
            f"{kv('Banned', banned)}\n{kv('Failed', failed)}\n{kv('Scanned', seen)}",
            expandable=True,
        ),
        parse_mode="html",
    )


async def _do_unbanall(e):
    client, chat = e.client, e.chat_id
    msg = await e.edit(
        f"{header('unbanall', '♻️')}\n\n" + quote("Fetching banned users…"),
        parse_mode="html",
    )
    rights = ChatBannedRights(until_date=None)
    freed = failed = seen = 0
    try:
        async for p in client.iter_participants(
            chat, filter=ChannelParticipantsKicked, aggressive=True
        ):
            seen += 1
            try:
                await client(EditBannedRequest(chat, p.id, rights))
                freed += 1
            except FloodWaitError as fe:
                await asyncio.sleep(fe.seconds + 1)
                try:
                    await client(EditBannedRequest(chat, p.id, rights))
                    freed += 1
                except Exception:
                    failed += 1
            except Exception as ex:
                log.debug(f"unban skip {p.id}: {ex}")
                failed += 1
            if seen % PROGRESS_EVERY == 0:
                await _progress(msg, "unbanall", freed + failed, seen, "♻️")
            await asyncio.sleep(BAN_DELAY)
    except ChatAdminRequiredError:
        return await msg.edit(
            f"{header('unbanall', '❌')}\n\n" + quote("Missing ban permission."),
            parse_mode="html",
        )

    await msg.edit(
        f"{header('unbanall done', '✅')}\n\n"
        + quote(f"{kv('Unbanned', freed)}\n{kv('Failed', failed)}", expandable=True),
        parse_mode="html",
    )
