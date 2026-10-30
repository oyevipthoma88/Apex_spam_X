"""Apex Spam X — unified raid engine (flood guard, lock, log channel)."""
import asyncio
import logging
import time
from random import choice

from telethon.errors import (
    ChatWriteForbiddenError,
    FloodWaitError,
    SlowModeWaitError,
)

from ApexSpam import HNDLR, OWNER_ID
from ApexSpam import fonts, roles
from ApexSpam import logger as xlog

log = logging.getLogger("ApexSpam.raid")

MAX_RAID = 500
DELAY = 0.12
ACTIVE = {}
COOLDOWN = {}


def is_active(chat_id):
    return chat_id in ACTIVE


def stop(chat_id):
    ACTIVE.pop(chat_id, None)


def _cooldown_left(client):
    until = COOLDOWN.get(id(client), 0)
    return max(0.0, until - time.time())


async def _send(client, chat_id, text):
    if _cooldown_left(client) > 0:
        return False
    try:
        await client.send_message(chat_id, text)
        return True
    except FloodWaitError as fe:
        COOLDOWN[id(client)] = time.time() + fe.seconds + 1
        log.warning(f"flood {fe.seconds}s client={id(client)}")
        return False
    except (ChatWriteForbiddenError, SlowModeWaitError) as e:
        log.warning(f"send blocked: {e}")
        return False
    except Exception as e:
        log.debug(f"send fail: {e}")
        return False


async def _chat_title(event):
    if event.is_private:
        return "DM"
    try:
        ch = await event.get_chat()
        return getattr(ch, "title", "unknown")
    except Exception:
        return "unknown"


def _usage(cmd_name):
    return (
        f"<b>Usage</b>\n"
        f"<code>{HNDLR}{cmd_name} COUNT @user</code>\n"
        f"<code>{HNDLR}{cmd_name} COUNT</code> (reply)"
    )


async def execute_raid(event, pack, cmd_name):
    if not await roles.can_use(event.sender_id):
        return
    if is_active(event.chat_id):
        return await event.reply(
            "⚠️ Raid already running here — send <code>.stop</code> to abort.",
            parse_mode="html",
        )

    parts = event.text.split(maxsplit=2)
    if len(parts) < 2:
        return await event.reply(_usage(cmd_name), parse_mode="html")
    try:
        count = int(parts[1])
    except ValueError:
        return await event.reply("❌ Count must be a number.", parse_mode="html")
    if not 1 <= count <= MAX_RAID:
        return await event.reply(f"❌ Count must be 1–{MAX_RAID}.", parse_mode="html")

    uid = name = None
    if len(parts) >= 3 and parts[2].strip():
        try:
            ent = await event.client.get_entity(parts[2].strip())
            uid, name = ent.id, (ent.first_name or "User")
        except Exception:
            return await event.reply("❌ Could not resolve user.", parse_mode="html")
    elif event.reply_to_msg_id:
        r = await event.get_reply_message()
        try:
            ent = await event.client.get_entity(r.sender_id)
            uid, name = ent.id, (ent.first_name or "User")
        except Exception:
            return await event.reply("❌ Could not resolve reply target.", parse_mode="html")
    else:
        return await event.reply(_usage(cmd_name), parse_mode="html")

    if await roles.role(uid) != roles.USER:
        return await event.reply("❌ Protected user (owner/sudo/admin).", parse_mode="html")

    if not pack:
        return await event.reply("❌ This pack is empty.", parse_mode="html")

    ACTIVE[event.chat_id] = True
    sent = 0
    mention = f"[{name}](tg://user?id={uid})"
    try:
        for _ in range(count):
            if not is_active(event.chat_id):
                break
            body = f"{mention} {fonts.fx(choice(pack))}"
            if await _send(event.client, event.chat_id, body):
                sent += 1
            await asyncio.sleep(DELAY)
    finally:
        stop(event.chat_id)

    try:
        await xlog.log_raid(
            user_id=event.sender_id,
            user_name=getattr(event.sender, "first_name", "User"),
            target_id=uid,
            target_name=name,
            chat_id=event.chat_id,
            chat_title=await _chat_title(event),
            cmd=cmd_name,
            count=sent,
        )
    except Exception:
        pass

    if sent == 0:
        await event.reply(
            "❌ All sends blocked (flood wait / no rights).",
            parse_mode="html",
        )
