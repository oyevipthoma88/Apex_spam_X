from telethon import events
from config import CLIENTS
from ApexSpam.patterns import cmd
from ApexSpam.raid_engine import execute_raid
from ApexSpam.data import HRAID


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=cmd("hraid"), incoming=True))
        async def hraid(e):
            await execute_raid(e, HRAID, "hraid")
