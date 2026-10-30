"""Apex Spam X — raid commands routed through hardened engine."""
import logging

from telethon import events

from ApexSpam import HNDLR, CLIENTS
from ApexSpam import data as D
from ApexSpam.raid_engine import execute_raid

log = logging.getLogger("ApexSpam.raid.mod")

PACKS = [
    ("raid", "RAID"),
    ("sraid", "SRAID"),
    ("craid", "CRAID"),
    ("qraid", "QRAID"),
    ("abuse", "ABUSE"),
    ("flirt", "FLIRT"),
    ("hraid", "HRAID"),
    ("bspam", "BDAY"),
    ("hrraid", "HRAID"),
    ("loveraid", "LOVERAID"),
    ("shayriraid", "SHAYRI_RAID"),
    ("gm", "GM"),
    ("ga", "GA"),
    ("gn", "GN"),
    ("emoji", "EMOJI"),
]


def _make(pack, name):
    async def handler(event):
        await execute_raid(event, pack, name)
    return handler


def register():
    for c in CLIENTS:
        for name, attr in PACKS:
            pack = getattr(D, attr, None) or []
            if not pack:
                log.warning(f"pack {attr} empty/missing -> {name} disabled")
                continue
            c.on(events.NewMessage(pattern=rf"^[\.!/]{name}(?: |$)"))(_make(pack, name))
