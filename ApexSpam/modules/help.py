from telethon import events, Button
from ApexSpam import HNDLR, CLIENTS
from ApexSpam.ui import header, quote, section, divider

MAIN = (
    f"{header('apex help', '⚡')}\n\n"
    + quote(f"<b>Prefix</b>  :  <code>{HNDLR}</code>")
    + "\n\n"
    + quote(
        f"{section('📂 CATEGORIES')}\n"
        "│  ◈ Raid   →  violent flood\n"
        "│  ◈ Spam   →  mass send\n"
        "│  ◈ Extra  →  utilities\n"
        "│  ◈ Admin  →  owner tools\n"
        "│  ◈ Sudo   →  manage access",
        expandable=True,
    )
    + f"\n\n{divider()}\n<i>Select a category</i> 👇"
)

MAIN_BTNS = [
    [Button.inline("🔫 Raid", data="help_raid"), Button.inline("💬 Spam", data="help_spam")],
    [Button.inline("🛠️ Extra", data="help_extra"), Button.inline("🛡️ Admin", data="help_admin")],
    [Button.inline("🔐 Sudo", data="help_sudo")],
]

PAGES = {
    "help_raid": header("raid", "🔫") + "\n\n" + quote(
        f"<code>{HNDLR}raid</code>   <code>{HNDLR}mraid</code>\n"
        f"<code>{HNDLR}sraid</code>  <code>{HNDLR}craid</code>\n"
        f"<code>{HNDLR}qraid</code>  <code>{HNDLR}loveraid</code>\n"
        f"<code>{HNDLR}hrraid</code> <code>{HNDLR}shayriraid</code>\n"
        f"<code>{HNDLR}abuse</code>  <code>{HNDLR}flirt</code>\n"
        f"<code>{HNDLR}hraid</code>  <code>{HNDLR}bspam</code>",
        expandable=True,
    ) + "\n\n" + quote(
        "<b>Format</b> : <code>CMD COUNT TARGET</code>\n"
        "<b>Target</b> : <code>@user</code> ya reply\n"
        "<b>Perm</b>   : <code>Sudo / Owner</code>"
    ),
    "help_spam": header("spam", "💬") + "\n\n" + quote(
        f"<code>{HNDLR}spam COUNT TEXT</code>\n"
        f"<code>{HNDLR}spam COUNT</code> (reply)\n"
        f"<code>{HNDLR}echo</code> (reply to user)\n"
        f"<code>{HNDLR}emoji EMOJI COUNT</code>\n"
        f"<code>{HNDLR}tagall MESSAGE</code>\n"
        f"<code>{HNDLR}gcast TEXT</code>",
        expandable=True,
    ),
    "help_extra": header("extra", "🛠️") + "\n\n" + quote(
        f"<code>{HNDLR}ping</code>     — latency\n"
        f"<code>{HNDLR}alive</code>    — alive card\n"
        f"<code>{HNDLR}id</code>       — user/chat id\n"
        f"<code>{HNDLR}join</code>     — join chat\n"
        f"<code>{HNDLR}leave</code>    — leave chat\n"
        f"<code>{HNDLR}purge</code>    — delete (reply)\n"
        f"<code>{HNDLR}gcdiag</code>   — group check",
        expandable=True,
    ),
    "help_admin": header("admin", "🛡️") + "\n\n" + quote(
        f"<code>{HNDLR}setpic</code>     — start photo\n"
        f"<code>{HNDLR}delpic</code>     — remove photo\n"
        f"<code>{HNDLR}setcaption</code> — custom caption\n"
        f"<code>{HNDLR}axlogs</code>     — heroku logs\n"
        f"<code>{HNDLR}axreboot</code>   — heroku restart",
        expandable=True,
    ) + "\n\n" + quote("<b>Perm</b> : <code>Owner</code>"),
    "help_sudo": header("sudo", "🔐") + "\n\n" + quote(
        f"<code>{HNDLR}addsudo ID</code>\n"
        f"<code>{HNDLR}delsudo ID</code>\n"
        f"<code>{HNDLR}listsudo</code>",
        expandable=True,
    ) + "\n\n" + quote("<i>MongoDB + env union — all bots share it.</i>"),
}


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=rf"\{HNDLR}help(?: |$)"))
        async def help_cmd(e):
            await e.reply(MAIN, buttons=MAIN_BTNS, parse_mode="html")

        @c.on(events.NewMessage(pattern=rf"\{HNDLR}help (\w+)(?: |$)"))
        async def help_text(e):
            key = f"help_{e.pattern_match.group(1).lower()}"
            if key in PAGES:
                await e.reply(PAGES[key], parse_mode="html")

        def _mk(txt):
            async def cb(e):
                await e.edit(txt, buttons=[[Button.inline("« Back", data="help_back")]], parse_mode="html")
            return cb

        for key, txt in PAGES.items():
            c.on(events.CallbackQuery(data=key.encode()))(_mk(txt))

        @c.on(events.CallbackQuery(data=b"help_back"))
        async def back(e):
            await e.edit(MAIN, buttons=MAIN_BTNS, parse_mode="html")
