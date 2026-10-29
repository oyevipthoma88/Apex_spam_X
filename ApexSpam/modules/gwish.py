from telethon import events
from config import CLIENTS
from ApexSpam.patterns import cmd
from ApexSpam.raid_engine import execute_raid
from ApexSpam.data import GM, GA, GN


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=cmd("gm"), incoming=True))
        async def gm(e):
            await execute_raid(e, GM, "gm")

        @c.on(events.NewMessage(pattern=cmd("ga"), incoming=True))
        async def ga(e):
            await execute_raid(e, GA, "ga")

        @c.on(events.NewMessage(pattern=cmd("gn"), incoming=True))
        async def gn(e):
            await execute_raid(e, GN, "gn")
