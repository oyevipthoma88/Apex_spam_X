import asyncio
from random import choice
from telethon.errors import FloodWaitError
from config import CMD_HNDLR, OWNER_ID
from models.sudo import is_sudo

MAX_RAID = 200

async def _has_perm(event) -> bool:
    if event.sender_id == OWNER_ID:
        return True
    return await is_sudo(event.sender_id)

async def execute_raid(event, messages: list[str], cmd_name: str):
    if not await _has_perm(event):
        return
    parts = event.text.split(maxsplit=2)
    usage = f"**Usage:**\n`{CMD_HNDLR}{cmd_name} <count> <user|reply>`"
    if len(parts) < 2:
        return await event.reply(usage, parse_mode="md")
    try:
        count = int(parts[1])
    except ValueError:
        return await event.reply("❌ Count must be a number.", parse_mode="md")
    if count < 1 or count > MAX_RAID:
        return await event.reply(f"❌ Count must be 1–{MAX_RAID}.", parse_mode="md")

    uid = name = None
    if len(parts) >= 3 and parts[2].strip():
        try:
            ent = await event.client.get_entity(parts[2].strip())
            uid, name = ent.id, (ent.first_name or "User")
        except Exception:
            return await event.reply("❌ Could not resolve user.", parse_mode="md")
    elif event.reply_to_msg_id:
        r = await event.get_reply_message()
        try:
            ent = await event.client.get_entity(r.sender_id)
            uid, name = ent.id, (ent.first_name or "User")
        except Exception:
            return await event.reply("❌ Could not resolve reply target.", parse_mode="md")
    else:
        return await event.reply(usage, parse_mode="md")

    mention = f"[{name}](tg://user?id={uid})"
    for _ in range(count):
        try:
            await event.client.send_message(event.chat_id, f"{mention} {choice(messages)}")
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except Exception:
            pass
        await asyncio.sleep(0.15)
