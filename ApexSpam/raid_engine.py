"""Apex Spam X — unified raid engine (Mongo + font + log channel)."""
import asyncio
from random import choice

from telethon.errors import FloodWaitError

from ApexSpam import HNDLR, OWNER_ID, SUDO_USERS
from ApexSpam import fonts
from ApexSpam import logger as xlog
from models.raid import get_raid_messages
from models.sudo import is_sudo
from ApexSpam.dedup import is_dup

MAX_RAID = 200
DELAY = 0.15


async def _authed(uid):
    if uid == OWNER_ID or uid in SUDO_USERS:
        return True
    try:
        return await is_sudo(uid)
    except Exception:
        return False


async def _pack(category, fallback):
    if category:
        try:
            msgs = await get_raid_messages(category)
            if msgs:
                return msgs + list(fallback)
        except Exception:
            pass
    return list(fallback)


async def _chat_title(event):
    if event.is_private:
        return "DM"
    try:
        chat = await event.get_chat()
        return getattr(chat, "title", "unknown")
    except Exception:
        return "unknown"


async def execute_raid(event, fallback, cmd_name, category=None):
    if is_dup(event.chat_id, event.id):
        return
    if not await _authed(event.sender_id):
        return

    parts = event.text.split(maxsplit=2)
    usage = (
        f"<b>Usage</b>\n<code>{HNDLR}{cmd_name} COUNT @user</code>\n"
        f"<code>{HNDLR}{cmd_name} COUNT</code> (reply)"
    )
    if len(parts) < 2:
        return await event.reply(usage, parse_mode="html")
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
        return await event.reply(usage, parse_mode="html")

    if uid == OWNER_ID:
        return await event.reply("❌ Can't raid the owner.", parse_mode="html")
    if await is_sudo(uid):
        return await event.reply("❌ Can't raid a sudo user.", parse_mode="html")

    pack = await _pack(category or cmd_name, fallback)
    if not pack:
        return await event.reply("❌ No messages in this pack.", parse_mode="html")

    safe_name = str(name).replace("[", "").replace("]", "").replace("(", "").replace(")", "")
    mention = f"[{safe_name}](tg://user?id={uid})"
    sent = 0
    for _ in range(count):
        body = f"{mention} {fonts.fx(choice(pack))}"
        try:
            await event.client.send_message(event.chat_id, body)
            sent += 1
        except FloodWaitError as fe:
            await asyncio.sleep(fe.seconds + 2)
        except Exception:
            pass
        await asyncio.sleep(DELAY)

    if sent == 0:
        await event.reply("❌ All sends failed — check bot rights.", parse_mode="html")
        return

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
