"""Apex Spam X — raid engine with live progress + stop."""
import asyncio
import logging
import time
from random import choice, uniform

from telethon.errors import ChatWriteForbiddenError, FloodWaitError, SlowModeWaitError

from ApexSpam import HNDLR, OWNER_ID
from ApexSpam import fonts, roles
from ApexSpam import logger as xlog
from ApexSpam import trace
from ApexSpam.ui import bread, quote, prog, pill, footer
from ApexSpam.buttons import ib

log = logging.getLogger("ApexSpam.raid")
MAX_RAID = 500
DELAY = 0.12
ACTIVE = {}
COOLDOWN = {}


def is_active(chat_id):
    return chat_id in ACTIVE


def stop(chat_id):
    ACTIVE.pop(chat_id, None)


def _cooldown(client):
    until = COOLDOWN.get(id(client), 0)
    return max(0.0, until - time.time())


async def _send(client, chat_id, text):
    if _cooldown(client) > 0:
        return False
    try:
        await client.send_message(chat_id, text)
        return True
    except FloodWaitError as fe:
        COOLDOWN[id(client)] = time.time() + fe.seconds + 1
        return False
    except (ChatWriteForbiddenError, SlowModeWaitError):
        return False
    except Exception:
        return False


async def _title(event):
    if event.is_private:
        return "DM"
    try:
        ch = await event.get_chat()
        return getattr(ch, "title", "unknown")
    except Exception:
        return "unknown"


def _status(cmd, cur, total):
    return (
        f"{bread('raid', cmd)}\n\n"
        + quote(f"{prog(cur, total)}\n{pill('running', 'warn')}", expandable=True)
        + f"\n{footer('send .stop to abort')}"
    )


def _usage(cmd):
    return (f"<b>Usage</b>\n"
            f"<code>{HNDLR}{cmd} COUNT @user</code>\n"
            f"<code>{HNDLR}{cmd} COUNT</code> (reply)")


async def execute_raid(event, pack, cmd_name):
    if not await roles.can_use(event.sender_id):
        return
    if is_active(event.chat_id):
        return await event.reply("⚠️ Raid already running here — send <code>.stop</code>.",
                                 parse_mode="html")

    parts = event.text.split(maxsplit=2)
    if len(parts) < 2:
        return await event.reply(_usage(cmd_name), parse_mode="html")
    try:
        count = int(parts[1])
    except ValueError:
        return await event.reply("❌ Count must be a number.", parse_mode="html")
    if not 1 <= count <= MAX_RAID:
        return await event.reply(f"❌ Count 1–{MAX_RAID}.", parse_mode="html")

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
        return await event.reply("❌ Protected user.", parse_mode="html")
    if not pack:
        return await event.reply("❌ Empty pack.", parse_mode="html")

    ACTIVE[event.chat_id] = True
    await asyncio.sleep(uniform(0.05, 0.4))  # stagger bots
    status = None
    try:
        status = await event.reply(
            _status(cmd_name, 0, count),
            buttons=[[ib("🛑 Stop", b"raid:stop", "danger")]],
            parse_mode="html",
        )
    except Exception:
        status = None

    sent = 0
    mention = f"[{name}](tg://user?id={uid})"
    step = max(1, count // 4)
    try:
        for i in range(count):
            if not is_active(event.chat_id):
                break
            body = f"{mention} {fonts.fx(choice(pack))}"
            if await _send(event.client, event.chat_id, body):
                sent += 1
            if status and (i + 1) % step == 0:
                try:
                    await status.edit(
                        _status(cmd_name, i + 1, count),
                        buttons=[[ib("🛑 Stop", b"raid:stop", "danger")]],
                        parse_mode="html",
                    )
                except Exception:
                    pass
            await asyncio.sleep(DELAY)
    finally:
        stop(event.chat_id)

    final = (
        f"{bread('raid', cmd_name, 'done')}\n\n"
        + quote(f"{pill('Completed', 'ok')}\n{prog(sent, count)}", expandable=True)
        + f"\n{footer()}"
    )
    if status:
        try:
            await status.edit(final, parse_mode="html")
        except Exception:
            pass
    else:
        await event.reply(final, parse_mode="html")

    try:
        await trace.log_raid(
            actor_id=event.sender_id,
            actor_name=getattr(event.sender, 'first_name', 'User'),
            target_id=uid, target_name=name,
            chat_id=event.chat_id, chat_title=await _title(event),
            cmd=cmd_name, count=sent,
        )
    except Exception:
        pass
    try:
        await xlog.log_raid(
            user_id=event.sender_id,
            user_name=getattr(event.sender, "first_name", "User"),
            target_id=uid, target_name=name,
            chat_id=event.chat_id, chat_title=await _title(event),
            cmd=cmd_name, count=sent,
        )
    except Exception:
        pass
