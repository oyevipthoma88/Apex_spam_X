from telethon import events
from config import CLIENTS
from ApexSpam.patterns import cmd
from ApexSpam.raid_engine import execute_raid
from ApexSpam.data import ABUSE


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=cmd("abuse"), incoming=True))
        async def h(e):
            await execute_raid(e, ABUSE, "abuse")
