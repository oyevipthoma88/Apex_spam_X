from telethon import events, Button
from config import CMD_HNDLR, CLIENTS

def _menu_text():
    return "**🤖 Apex Spam X — Help Menu**\n\nChoose a category below:", [
        [Button.inline("🔫 Raids", b"help_raid"), Button.inline("🛠️ Utility", b"help_util")],
        [Button.inline("🔐 Sudo", b"help_sudo")],
    ]

RAID_TXT = f"""**🔫 Raid Commands** (sudo)

`{CMD_HNDLR}raid <count> <user|reply>`
`{CMD_HNDLR}mraid <count> <user|reply>`
`{CMD_HNDLR}sraid <count> <user|reply>`
`{CMD_HNDLR}craid <count> <user|reply>`
`{CMD_HNDLR}qraid <count> <user|reply>`
`{CMD_HNDLR}loveraid <count> <user|reply>`
`{CMD_HNDLR}hrraid <count> <user|reply>`
`{CMD_HNDLR}shayriraid <count> <user|reply>`
"""

UTIL_TXT = f"""**🛠️ Utility Commands** (sudo)

`{CMD_HNDLR}ping` — latency + uptime
`{CMD_HNDLR}spam <count> <text>` — spam text
`{CMD_HNDLR}echo <text>` — repeat text
`{CMD_HNDLR}emoji <emoji> <count>` — emoji flood
`{CMD_HNDLR}purge` — delete (reply to start)
`{CMD_HNDLR}tagall <msg>` — tag everyone
`{CMD_HNDLR}kick <user|reply>` — kick member
`{CMD_HNDLR}gcast <text>` — broadcast to groups
"""

SUDO_TXT = f"""**🔐 Sudo Commands** (Owner only)

`{CMD_HNDLR}addsudo <user|reply|id>`
`{CMD_HNDLR}delsudo <user|reply|id>`
`{CMD_HNDLR}listsudo` — view all sudo
"""

def register():
    pat = rf"\{CMD_HNDLR}help(?: |$)"
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=pat))
        async def h(e):
            text, btns = _menu_text()
            await e.reply(text, buttons=btns, parse_mode="md")

        @c.on(events.CallbackQuery(data=b"help_raid"))
        async def cb_r(e):
            await e.edit(RAID_TXT, buttons=[[Button.inline("« Back", b"help_back")]], parse_mode="md")

        @c.on(events.CallbackQuery(data=b"help_util"))
        async def cb_u(e):
            await e.edit(UTIL_TXT, buttons=[[Button.inline("« Back", b"help_back")]], parse_mode="md")

        @c.on(events.CallbackQuery(data=b"help_sudo"))
        async def cb_s(e):
            await e.edit(SUDO_TXT, buttons=[[Button.inline("« Back", b"help_back")]], parse_mode="md")

        @c.on(events.CallbackQuery(data=b"help_back"))
        async def cb_b(e):
            text, btns = _menu_text()
            await e.edit(text, buttons=btns, parse_mode="md")
