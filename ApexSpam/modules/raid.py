"""Apex Spam X — raid commands (unified engine, all in one)."""
from telethon import events

from ApexSpam import HNDLR, CLIENTS
from ApexSpam.raid_engine import execute_raid
from ApexSpam.data import RAID, SRAID, CRAID, QRAID

CMD_PACKS = [
    ("raid", RAID),
    ("mraid", RAID),
    ("sraid", SRAID),
    ("craid", CRAID),
    ("qraid", QRAID),
]


def _make_handler(pack, name):
    async def handler(event):
        await execute_raid(event, pack, name)
    return handler


def register():
    for c in CLIENTS:
        for name, pack in CMD_PACKS:
            c.on(events.NewMessage(pattern=rf"^[\.!/]{name}(?: |$)"))(
                _make_handler(pack, name)
            )
