from telethon import events
from config import CLIENTS
from ApexSpam.patterns import cmd
from ApexSpam.raid_engine import execute_raid
from ApexSpam.data import HRAID, BSPAM

def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=cmd("hraid"), incoming=True))
        async def hraid(e):
            await execute_raid(e, HRAID, "hraid", "hraid")

        @c.on(events.NewMessage(pattern=cmd("bspam"), incoming=True))
        async def bspam(e):
            await execute_raid(e, BSPAM, "bspam", "bspam")
