from telethon import events
from config import CMD_HNDLR, CLIENTS
from ApexSpam.raid_engine import execute_raid
from ApexSpam.data import HRRAID

def register():
    pat = rf"\\{CMD_HNDLR}hrraid(?: |\$)"
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=pat))
        async def h(e, _v=HRRAID, _n="hrraid"):
            await execute_raid(e, _v, _n)
