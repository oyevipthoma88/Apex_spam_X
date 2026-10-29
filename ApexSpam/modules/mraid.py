from telethon import events
from config import CLIENTS
from ApexSpam.patterns import cmd
from ApexSpam.raid_engine import execute_raid
from ApexSpam.data import RAID

def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=cmd("mraid"), incoming=True))
        async def h(e, _v=RAID, _n="mraid"):
            await execute_raid(e, _v, _n, "mraid")
