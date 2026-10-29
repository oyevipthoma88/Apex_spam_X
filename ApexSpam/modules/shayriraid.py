from telethon import events
from config import CMD_HNDLR, CLIENTS
from ApexSpam.raid_engine import execute_raid
from ApexSpam.data import SHAYRI_RAID

def register():
    pat = rf"\\{CMD_HNDLR}shayriraid(?: |\$)"
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=pat))
        async def h(e, _v=SHAYRI_RAID, _n="shayriraid"):
            await execute_raid(e, _v, _n)
