from telethon import events

from ApexSpam import HNDLR, CLIENTS
from ApexSpam import roles, respond
from ApexSpam.ui import bread, quote, divider, footer, pill, kv, join_rows
from ApexSpam.buttons import ib, copy_btn, nav, grid

PAGES = {
    "help_raid": ("raid", "🔫",
        "raid sraid craid qraid abuse flirt hraid bspam hrraid loveraid shayriraid gm ga gn emoji",
        "Sudo / Owner"),
    "help_spam": ("spam", "💬", "spam", "Sudo / Owner"),
    "help_extra": ("extra", "🛠️", "ping alive id leave gcdiag rraid drraid stop", "everyone"),
    "help_admin": ("admin", "🛡️", "setpic delpic setcaption font axlogs axreboot reboot", "Owner"),
    "help_mod": ("moderation", "⚔️", "banall unbanall nc", "Owner / Sudo"),
    "help_sudo": ("sudo", "🔐", "addsudo delsudo sudolist addadmin deladmin listadmin", "Owner / Sudo"),
    "help_custom": ("custom", "🧩", "setcmd delcmd mycmds", "everyone"),
}


def _page(key):
    name, emoji, cmds, perm = PAGES[key]
    cmd_list = cmds.split()
    body = "\n".join(f"<code>{HNDLR}{c}</code>" for c in cmd_list)
    text = (
        f"{bread('help', name)}\n\n"
        + quote(body, expandable=True)
        + "\n\n"
        + quote(f"{kv('Perm', perm)}")
    )
    rows = []
    cb = copy_btn("📋 Copy commands", "\n".join(f"{HNDLR}{c}" for c in cmd_list))
    if cb:
        rows.append([cb])
    rows.append(nav(b"help:back"))
    return text, join_rows(rows)


async def _menu(uid):
    r = await roles.role(uid)
    label = {"owner": "Owner", "sudo": "Sudo", "admin": "Admin", "user": "User"}[r]
    text = (
        f"{bread('help', 'home')}\n\n"
        + quote(f"{pill(label, 'ok' if r != 'user' else 'info')}\n"
                f"{kv('Prefix', HNDLR + '  !  /')}", expandable=True)
        + f"\n{divider()}\n<i>Pick a category</i> 👇\n{footer()}"
    )
    buttons = []
    if r in ("owner", "sudo", "admin"):
        buttons += [ib("🔫 Raid", b"help_raid", "primary"),
                    ib("💬 Spam", b"help_spam", "primary")]
    buttons += [ib("🛠️ Extra", b"help_extra", "primary"),
                ib("🧩 Custom", b"help_custom", "success")]
    if r in ("owner", "sudo"):
        buttons.append(ib("⚔️ Moderation", b"help_mod", "danger"))
    if r == "owner":
        buttons += [ib("🛡️ Admin", b"help_admin", "danger"),
                    ib("🔐 Sudo", b"help_sudo", "success")]
    rows = grid(buttons, 2)
    rows.append([ib("✖ Close", b"close", "danger")])
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
            allow = {
                "help_raid": r in ("owner", "sudo", "admin"),
                "help_spam": r in ("owner", "sudo", "admin"),
                "help_extra": True,
                "help_custom": True,
                "help_mod": r in ("owner", "sudo"),
                "help_admin": r == "owner",
                "help_sudo": r in ("owner", "sudo"),
            }
            if key in PAGES and allow.get(key):
                text, rows = _page(key)
                await e.reply(text, buttons=rows, parse_mode="html")

        for key in PAGES:
            def _mk(k):
                async def cb(e):
                    await respond.ack(e)
                    text, rows = _page(k)
                    await respond.edit(e, text, rows)
                return cb
            c.on(events.CallbackQuery(data=key.encode()))(_mk(key))

        @c.on(events.CallbackQuery(data=b"help:back"))
        async def back(e):
            await respond.ack(e)
            text, rows = await _menu(e.sender_id)
            await respond.edit(e, text, rows)

        @c.on(events.CallbackQuery(data=b"close"))
        async def close(e):
            await respond.ack(e)
            try:
                await e.delete()
            except Exception:
                pass
