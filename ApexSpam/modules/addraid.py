"""Apex Spam X — global raid pack management (Mongo)."""
from telethon import events

from ApexSpam import HNDLR, CLIENTS
from ApexSpam import roles
from ApexSpam.ui import header, quote, kv
from models.raid import get_raid_messages, set_raid_messages
from ApexSpam.data import (
    RAID, SRAID, CRAID, QRAID, ABUSE, FLIRT,
    HRAID, LOVERAID, GM, GA, GN, EMOJI,
)

PACKS = {
    "raid": RAID, "sraid": SRAID, "craid": CRAID, "qraid": QRAID,
    "abuse": ABUSE, "flirt": FLIRT, "hraid": HRAID, "hrraid": HRAID,
    "loveraid": LOVERAID, "gm": GM, "ga": GA, "gn": GN, "emoji": EMOJI,
}


async def _perm(e):
    return await roles.can_use(e.sender_id)


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=r"^[\.!/]addraid(?: |$)"))
        async def addraid(e):
            if not await _perm(e):
                return
            parts = e.text.split(maxsplit=2)
            if len(parts) < 3:
                return await e.reply(
                    f"{header('addraid', '⚠️')}\n\n"
                    + quote(f"<code>{HNDLR}addraid CATEGORY TEXT</code>\n"
                            f"Categories: {', '.join(PACKS)}"),
                    parse_mode="html",
                )
            cat, text = parts[1].lower(), parts[2][:500]
            if cat not in PACKS:
                return await e.reply("❌ Invalid category.", parse_mode="html")
            cur = await get_raid_messages(cat) or []
            if text not in cur:
                cur.append(text)
            await set_raid_messages(cat, cur)
            await e.reply(
                f"{header('raid added', '✅')}\n\n"
                + quote(f"{kv('Category', cat)}\n{kv('Total', len(cur))}", expandable=True),
                parse_mode="html",
            )

        @c.on(events.NewMessage(pattern=r"^[\.!/]delraid(?: |$)"))
        async def delraid(e):
            if not await _perm(e):
                return
            parts = e.text.split(maxsplit=2)
            if len(parts) < 3:
                return await e.reply(f"<code>{HNDLR}delraid CATEGORY INDEX</code>", parse_mode="html")
            cat = parts[1].lower()
            try:
                idx = int(parts[2])
            except ValueError:
                return await e.reply("❌ Index must be number.", parse_mode="html")
            cur = await get_raid_messages(cat) or []
            if idx < 0 or idx >= len(cur):
                return await e.reply("❌ Index out of range.", parse_mode="html")
            removed = cur.pop(idx)
            await set_raid_messages(cat, cur)
            await e.reply(
                f"{header('raid removed', '🗑️')}\n\n"
                + quote(f"{kv('Removed', removed[:60])}\n{kv('Left', len(cur))}"),
                parse_mode="html",
            )

        @c.on(events.NewMessage(pattern=r"^[\.!/]listraid(?: |$)"))
        async def listraid(e):
            if not await _perm(e):
                return
            parts = e.text.split(maxsplit=1)
            cat = parts[1].lower() if len(parts) > 1 else ""
            if cat not in PACKS:
                return await e.reply(f"<code>{HNDLR}listraid CATEGORY</code>", parse_mode="html")
            cur = await get_raid_messages(cat) or []
            body = "\n".join(f"<code>{i}</code>. {x[:60]}" for i, x in enumerate(cur[:20])) or "<i>none</i>"
            await e.reply(
                f"{header(f'{cat} pack', '📋')}\n\n"
                + quote(f"<b>Mongo</b> : <code>{len(cur)}</code>\n<b>Fallback</b> : <code>{len(PACKS[cat])}</code>")
                + f"\n\n{body}",
                parse_mode="html",
            )
