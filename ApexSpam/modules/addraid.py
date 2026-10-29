from telethon import events
from config import CLIENTS, OWNER_ID, CMD_HNDLR
from ApexSpam.patterns import cmd
from models.sudo import is_sudo
from models.raid import get_raid_messages, set_raid_messages

CATEGORIES = [
    "raid", "mraid", "sraid", "craid", "qraid", "loveraid",
    "hrraid", "shayriraid", "abuse", "flirt", "hraid", "bspam",
    "gm", "ga", "gn",
]


async def _perm(e):
    return e.sender_id == OWNER_ID or await is_sudo(e.sender_id)


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=cmd("addraid")))
        async def addraid(e):
            if not await _perm(e):
                return
            parts = e.text.split(maxsplit=2)
            if len(parts) < 3:
                return await e.reply(
                    f"Usage: `{CMD_HNDLR}addraid <category> <message>`\n"
                    f"Categories: {', '.join(CATEGORIES)}",
                    parse_mode="md",
                )
            cat, msg = parts[1].lower(), parts[2]
            if cat not in CATEGORIES:
                return await e.reply(f"❌ Invalid category. Use: {', '.join(CATEGORIES)}", parse_mode="md")
            current = await get_raid_messages(cat) or []
            current.append(msg)
            await set_raid_messages(cat, current)
            await e.reply(f"✅ Added to `{cat}` (total {len(current)})", parse_mode="md")

        @c.on(events.NewMessage(pattern=cmd("delraid")))
        async def delraid(e):
            if not await _perm(e):
                return
            parts = e.text.split(maxsplit=2)
            if len(parts) < 3:
                return await e.reply(f"Usage: `{CMD_HNDLR}delraid <category> <index>`", parse_mode="md")
            cat = parts[1].lower()
            try:
                idx = int(parts[2])
            except ValueError:
                return await e.reply("❌ Index must be number.", parse_mode="md")
            current = await get_raid_messages(cat) or []
            if idx < 0 or idx >= len(current):
                return await e.reply(f"❌ Index out of range (0–{len(current)-1}).", parse_mode="md")
            removed = current.pop(idx)
            await set_raid_messages(cat, current)
            await e.reply(f"🗑️ Removed: `{removed[:40]}`", parse_mode="md")

        @c.on(events.NewMessage(pattern=cmd("listraid")))
        async def listraid(e):
            if not await _perm(e):
                return
            parts = e.text.split(maxsplit=1)
            if len(parts) < 2:
                return await e.reply(f"Usage: `{CMD_HNDLR}listraid <category>`", parse_mode="md")
            cat = parts[1].lower()
            msgs = await get_raid_messages(cat) or []
            if not msgs:
                return await e.reply(f"`{cat}` has no custom messages (default use ho raha hai).", parse_mode="md")
            text = f"**📋 `{cat}` messages ({len(msgs)}):**\n" + "\n".join(
                f"`{i}`. {m[:60]}" for i, m in enumerate(msgs)
            )
            await e.reply(text, parse_mode="md")
