from telethon import events, Button
from ApexSpam import HNDLR, X1, X2, X3, X4, X5, X6, X7, X8, X9, X10
from ApexSpam.ui import header

MAIN = (
    f"{header('apex help', '⚡')}\n\n"
    f"**Prefix** : `{HNDLR}`\n\n"
    "╭─〔 **📂 CATEGORIES** 〕─╮\n"
    "│  ◈ Raid      →  violent flood\n"
    "│  ◈ Spam      →  mass send\n"
    "│  ◈ Extra     →  utilities\n"
    "│  ◈ Admin     →  owner tools\n"
    "│  ◈ Sudo      →  manage access\n"
    "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
    "_Select a category_ 👇"
)

MAIN_BTNS = [
    [Button.inline("🔫 Raid", data="help_raid"), Button.inline("💬 Spam", data="help_spam")],
    [Button.inline("🛠️ Extra", data="help_extra"), Button.inline("🛡️ Admin", data="help_admin")],
    [Button.inline("🔐 Sudo", data="help_sudo")],
]

PAGES = {
    "help_raid": (
        f"{header('raid', '🔫')}\n\n"
        f"`{HNDLR}raid`    `{HNDLR}mraid`\n"
        f"`{HNDLR}sraid`   `{HNDLR}craid`\n"
        f"`{HNDLR}qraid`   `{HNDLR}loveraid`\n"
        f"`{HNDLR}hrraid`  `{HNDLR}shayriraid`\n"
        f"`{HNDLR}abuse`   `{HNDLR}flirt`\n"
        f"`{HNDLR}hraid`   `{HNDLR}bspam`\n\n"
        f"**Format** : `<cmd> <count> <user|reply>`\n"
        f"**Perm**   : `Sudo / Owner`"
    ),
    "help_spam": (
        f"{header('spam', '💬')}\n\n"
        f"`{HNDLR}spam <count> <text|reply>`\n"
        f"`{HNDLR}echo <text>`\n"
        f"`{HNDLR}emoji <emoji> <count>`\n"
        f"`{HNDLR}tagall <msg>`\n"
        f"`{HNDLR}gcast <text>`\n\n"
        f"**Perm** : `Sudo / Owner`"
    ),
    "help_extra": (
        f"{header('extra', '🛠️')}\n\n"
        f"`{HNDLR}ping`      —  latency\n"
        f"`{HNDLR}apxping`   —  premium latency card\n"
        f"`{HNDLR}alive`     —  alive card\n"
        f"`{HNDLR}id`        —  user/chat id\n"
        f"`{HNDLR}join`      —  join chat\n"
        f"`{HNDLR}leave`     —  leave chat\n"
        f"`{HNDLR}purge`     —  delete (reply)"
    ),
    "help_admin": (
        f"{header('admin', '🛡️')}\n\n"
        f"`{HNDLR}axlogs`    —  heroku logs file\n"
        f"`{HNDLR}axreboot`  —  heroku restart\n\n"
        f"**Perm** : `Owner`"
    ),
    "help_sudo": (
        f"{header('sudo', '🔐')}\n\n"
        f"`{HNDLR}addsudo <id|reply|@u>`\n"
        f"`{HNDLR}delsudo <id|reply|@u>`\n"
        f"`{HNDLR}listsudo`\n\n"
        "_MongoDB + env union._"
    ),
}


def register():
    for c in [X1, X2, X3, X4, X5, X6, X7, X8, X9, X10]:
        @c.on(events.NewMessage(pattern=rf"\{HNDLR}help(?: |$)"))
        async def help_cmd(e):
            await e.reply(MAIN, buttons=MAIN_BTNS, parse_mode="md")

        @c.on(events.NewMessage(pattern=rf"\{HNDLR}help (\w+)(?: |$)"))
        async def help_text(e):
            key = f"help_{e.pattern_match.group(1).lower()}"
            if key in PAGES:
                await e.reply(PAGES[key], parse_mode="md")

        for key, txt in PAGES.items():
            @c.on(events.CallbackQuery(data=key.encode()))
            async def cb(e, _t=txt):
                await e.edit(_t, buttons=[[Button.inline("« Back", data="help_back")]], parse_mode="md")

        @c.on(events.CallbackQuery(data=b"help_back"))
        async def back(e):
            await e.edit(MAIN, buttons=MAIN_BTNS, parse_mode="md")
