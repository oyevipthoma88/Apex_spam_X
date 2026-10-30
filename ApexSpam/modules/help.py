from telethon import events
from ApexSpam import HNDLR, CLIENTS
from ApexSpam.ui import header, quote, divider, footer
from ApexSpam.buttons import ib
from ApexSpam import roles

PAGES = {
    "help_raid": ("raid", "🔫",
        "raid sraid craid qraid abuse flirt hraid bspam hrraid loveraid shayriraid gm ga gn emoji",
        "`CMD COUNT @user` / reply"),
    "help_spam": ("spam", "💬", "spam", "`spam COUNT TEXT` / reply"),
    "help_extra": ("extra", "🛠️", "ping alive id leave gcdiag rraid drraid stop", "basic"),
    "help_admin": ("admin", "🛡️", "setpic delpic setcaption font axlogs axreboot reboot", "Owner"),
    "help_mod": ("moderation", "⚔️", "banall unbanall nc", "Owner / Sudo"),
    "help_sudo": ("sudo", "🔐", "addsudo delsudo sudolist addadmin deladmin listadmin", "Owner / Sudo"),
    "help_custom": ("custom", "🧩", "setcmd delcmd mycmds", "everyone"),
}


def _page(key):
    name, emoji, cmds, perm = PAGES[key]
    lines = "\n".join(f"<code>{HNDLR}{x}</code>" for x in cmds.split())
    return (
        f"{header(name, emoji)}\n\n"
        + quote(lines, expandable=True)
        + "\n\n"
        + quote(f"<b>Perm</b> : <code>{perm}</code>")
    )


async def _menu(uid):
    r = await roles.role(uid)
    role_label = {"owner": "👑 Owner", "sudo": "🛡️ Sudo",
                  "admin": "👤 Admin", "user": "👤 User"}[r]
    text = (
        f"{header('apex help', '⚡')}\n\n"
        + quote(f"<b>Prefix</b> : <code>{HNDLR}</code>\n<b>Role</b> : {role_label}")
        + f"\n\n{divider()}\n<i>Select a category</i> 👇\n{footer()}"
    )
    rows = []
    if r in ("owner", "sudo", "admin"):
        rows.append([ib("🔫 Raid", b"help_raid", "primary"),
                     ib("💬 Spam", b"help_spam", "primary")])
    rows.append([ib("🛠️ Extra", b"help_extra", "primary"),
                 ib("🧩 Custom", b"help_custom", "success")])
    if r in ("owner", "sudo"):
        rows.append([ib("⚔️ Moderation", b"help_mod", "danger")])
    if r == "owner":
        rows.append([ib("🛡️ Admin", b"help_admin", "danger"),
                     ib("🔐 Sudo", b"help_sudo", "success")])
    return text, rows


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=r"^[\.!/]help(?: |$)"))
        async def help_cmd(e):
            text, rows = await _menu(e.sender_id)
            await e.reply(text, buttons=rows, parse_mode="html")

        @c.on(events.NewMessage(pattern=r"^[\.!/]help (\w+)(?: |$)"))
        async def help_text(e):
            key = f"help_{e.pattern_match.group(1).lower()}"
            r = await roles.role(e.sender_id)
            allowed = {
                "help_raid": r in ("owner", "sudo", "admin"),
                "help_spam": r in ("owner", "sudo", "admin"),
                "help_extra": True,
                "help_custom": True,
                "help_mod": r in ("owner", "sudo"),
                "help_admin": r == "owner",
                "help_sudo": r in ("owner", "sudo"),
            }
            if key in PAGES and allowed.get(key):
                await e.reply(_page(key), parse_mode="html")

        def _cb(key):
            async def h(e):
                await e.edit(_page(key),
                             buttons=[[ib("« Back", b"help_back", "primary")]],
                             parse_mode="html")
            return h

        for key in PAGES:
            c.on(events.CallbackQuery(data=key.encode()))(_cb(key))

        @c.on(events.CallbackQuery(data=b"help_back"))
        async def back(e):
            text, rows = await _menu(e.sender_id)
            await e.edit(text, buttons=rows, parse_mode="html")
