from telethon import events
from config import CMD_HNDLR, CLIENTS
from ApexSpam.raid_engine import execute_raid
from ApexSpam.data import RAID

def register():
    pat = rf"\\{CMD_HNDLR}mraid(?: |\$)"
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=pat))
        async def h(e, _v=RAID, _n="mraid"):
            await execute_raid(e, _v, _n)
