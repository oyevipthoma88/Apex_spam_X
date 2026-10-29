from telethon import events, Button
from ApexSpam import HNDLR, X1, X2, X3, X4, X5, X6, X7, X8, X9, X10

MAIN = (
    "╭━━━━━━━━━━━━━━━━━━━╮\n"
    "   ⚡  **H E L P   M E N U**  ⚡\n"
    "╰━━━━━━━━━━━━━━━━━━━╯\n\n"
    f"**Prefix** : `{HNDLR}`\n\n"
    "╭─〔 **📂 CATEGORIES** 〕─╮\n"
    "│  ◈ Raid      →  `/help raid`\n"
    "│  ◈ Spam      →  `/help spam`\n"
    "│  ◈ Extra     →  `/help extra`\n"
    "│  ◈ Sudo      →  `/help sudo`\n"
    "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
    "_Select below_ 👇"
)

MAIN_BTNS = [
    [Button.inline("🔫 Raid", data="help_raid"), Button.inline("💬 Spam", data="help_spam")],
    [Button.inline("🛠️ Extra", data="help_extra"), Button.inline("🔐 Sudo", data="help_sudo")],
]

PAGES = {
    "help_raid": (
        "╭━━━━━━━━━━━━━━━━━━━╮\n"
        "   🔫  **R A I D**  🔫\n"
        "╰━━━━━━━━━━━━━━━━━━━╯\n\n"
        f"`{HNDLR}raid`    `{HNDLR}mraid`\n"
        f"`{HNDLR}sraid`   `{HNDLR}craid`\n"
        f"`{HNDLR}qraid`   `{HNDLR}loveraid`\n"
        f"`{HNDLR}hrraid`  `{HNDLR}shayriraid`\n"
        f"`{HNDLR}abuse`   `{HNDLR}flirt`\n"
        f"`{HNDLR}hraid`   `{HNDLR}bspam`\n\n"
        "**Format** :  `<cmd> <count> <user|reply>`\n"
        "**Perm**   :  `Sudo / Owner`"
    ),
    "help_spam": (
        "╭━━━━━━━━━━━━━━━━━━━╮\n"
        "   💬  **S P A M**  💬\n"
        "╰━━━━━━━━━━━━━━━━━━━╯\n\n"
        f"`{HNDLR}spam <count> <text|reply>`\n"
        f"`{HNDLR}echo <text>`\n"
        f"`{HNDLR}emoji <emoji> <count>`\n"
        f"`{HNDLR}tagall <msg>`\n"
        f"`{HNDLR}gcast <text>`\n\n"
        "**Perm** :  `Sudo / Owner`"
    ),
    "help_extra": (
        "╭━━━━━━━━━━━━━━━━━━━╮\n"
        "   🛠️  **E X T R A**  🛠️\n"
        "╰━━━━━━━━━━━━━━━━━━━╯\n\n"
        f"`{HNDLR}ping`     —  latency\n"
        f"`{HNDLR}id`       —  user / chat id\n"
        f"`{HNDLR}stats`    —  uptime & info\n"
        f"`{HNDLR}join`     —  join chat\n"
        f"`{HNDLR}leave`    —  leave chat\n"
        f"`{HNDLR}purge`    —  delete (reply)\n"
        f"`{HNDLR}reboot`   —  restart (owner)\n"
        f"`{HNDLR}logs`     —  heroku logs"
    ),
    "help_sudo": (
        "╭━━━━━━━━━━━━━━━━━━━╮\n"
        "   🔐  **S U D O**  🔐\n"
        "╰━━━━━━━━━━━━━━━━━━━╯\n\n"
        f"`{HNDLR}addsudo <id|reply|@u>`\n"
        f"`{HNDLR}delsudo <id|reply|@u>`\n"
        f"`{HNDLR}listsudo`\n\n"
        "_Mongo + ENV union works._"
    ),
}


def register():
    for c in [X1, X2, X3, X4, X5, X6, X7, X8, X9, X10]:
        @c.on(events.NewMessage(pattern=rf"\{HNDLR}help(?: |$)"))
        async def help_cmd(e):
            await e.reply(MAIN, buttons=MAIN_BTNS, parse_mode="md")

        for key, txt in PAGES.items():
            @c.on(events.CallbackQuery(data=key.encode()))
            async def cb(e, _t=txt):
                await e.edit(_t, buttons=[[Button.inline("« Back", data="help_back")]], parse_mode="md")

        @c.on(events.CallbackQuery(data=b"help_back"))
        async def back(e):
            await e.edit(MAIN, buttons=MAIN_BTNS, parse_mode="md")
