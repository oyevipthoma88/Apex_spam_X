"""Apex Spam X — ALL raid commands, one engine, no duplicates."""
from telethon import events

from ApexSpam import HNDLR, CLIENTS
from ApexSpam.raid_engine import execute_raid
from ApexSpam.data import (
    RAID, SRAID, CRAID, QRAID, ABUSE, FLIRT,
    HRAID, LOVERAID, GM, GA, GN, EMOJI,
)

PACKS = [
    ("raid", RAID), ("sraid", SRAID), ("craid", CRAID), ("qraid", QRAID),
    ("abuse", ABUSE), ("flirt", FLIRT), ("hraid", HRAID), ("hrraid", HRAID),
    ("loveraid", LOVERAID), ("gm", GM), ("ga", GA), ("gn", GN), ("emoji", EMOJI),
]


def _make(pack, name):
    async def handler(event):
        await execute_raid(event, pack, name)
    return handler


def register():
    for c in CLIENTS:
        for name, pack in PACKS:
            c.on(events.NewMessage(pattern=rf"^[\.!/]{name}(?: |$)"))(_make(pack, name))
