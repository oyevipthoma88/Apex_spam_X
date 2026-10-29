from telethon import events, Button
from ApexSpam import HNDLR, OWNER_ID, CLIENTS, SUDO_USERS
from ApexSpam.ui import header, quote, section, divider


def _is_owner(uid): return uid == OWNER_ID
def _is_sudo(uid):  return uid in SUDO_USERS


def _menu_text(uid):
    if _is_owner(uid):
        role = "👑 Owner"
    elif _is_sudo(uid):
        role = "🛡️ Sudo"
    else:
        role = "👤 User"
    return (
        f"{header('apex help', '⚡')}\n\n"
        + quote(f"<b>Prefix</b>  :  <code>{HNDLR}</code>\n<b>Role</b>    :  {role}")
        + f"\n\n{divider()}\n<i>Select a category</i> 👇"
    )


def _menu_buttons(uid):
    buttons = []
    if _is_owner(uid) or _is_sudo(uid):
        buttons.append([Button.inline("🔫 Raid", data="help_raid"),
                        Button.inline("💬 Spam", data="help_spam")])
    buttons.append([Button.inline("🛠️ Extra", data="help_extra")])
    if _is_owner(uid):
        buttons.append([Button.inline("🛡️ Admin", data="help_admin"),
                        Button.inline("🔐 Sudo", data="help_sudo")])
        buttons.append([Button.inline("🎨 Font", data="help_font")])
    return buttons


PAGES = {
    "help_raid": header("raid", "🔫") + "\n\n" + quote(
        f"<code>{HNDLR}raid</code>    <code>{HNDLR}mraid</code>\n"
        f"<code>{HNDLR}sraid</code>   <code>{HNDLR}craid</code>\n"
        f"<code>{HNDLR}qraid</code>   <code>{HNDLR}loveraid</code>\n"
        f"<code>{HNDLR}hrraid</code>  <code>{HNDLR}shayriraid</code>\n"
        f"<code>{HNDLR}abuse</code>   <code>{HNDLR}flirt</code>\n"
        f"<code>{HNDLR}hraid</code>   <code>{HNDLR}bspam</code>",
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
        f"<code>{HNDLR}purge</code>    — delete (reply)",
        expandable=True,
    ),
    "help_admin": header("admin", "🛡️") + "\n\n" + quote(
        f"<code>{HNDLR}setpic</code>     — start photo\n"
        f"<code>{HNDLR}delpic</code>     — remove photo\n"
        f"<code>{HNDLR}setcaption</code> — custom caption\n"
        f"<code>{HNDLR}font</code>       — font studio\n"
        f"<code>{HNDLR}axlogs</code>     — heroku logs\n"
        f"<code>{HNDLR}axreboot</code>   — heroku restart\n"
        f"<code>{HNDLR}gcdiag</code>     — group check",
        expandable=True,
    ) + "\n\n" + quote("<b>Perm</b> : <code>Owner only</code>"),
    "help_sudo": header("sudo", "🔐") + "\n\n" + quote(
        f"<code>{HNDLR}addsudo ID</code>\n"
        f"<code>{HNDLR}delsudo ID</code>\n"
        f"<code>{HNDLR}listsudo</code>",
        expandable=True,
    ) + "\n\n" + quote("<i>Mongo + env union — global.</i>"),
    "help_font": header("font", "🎨") + "\n\n" + quote(
        f"<code>{HNDLR}font</code>          — open studio\n"
        f"<code>{HNDLR}font bold</code>     — set by name\n"
        f"<code>{HNDLR}font 1</code>        — set by index\n\n"
        "All bot messages instantly use selected font.",
        expandable=True,
    ) + "\n\n" + quote("<b>Perm</b> : <code>Owner only</code>"),
}


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=rf"\{HNDLR}help(?: |$)"))
        async def help_cmd(e):
            await e.reply(_menu_text(e.sender_id),
                          buttons=_menu_buttons(e.sender_id),
                          parse_mode="html")

        @c.on(events.NewMessage(pattern=rf"\{HNDLR}help (\w+)(?: |$)"))
        async def help_text(e):
            key = f"help_{e.pattern_match.group(1).lower()}"
            uid = e.sender_id
            if key in ("help_admin", "help_sudo", "help_font") and not _is_owner(uid):
                return
            if key in ("help_raid", "help_spam") and not (_is_owner(uid) or _is_sudo(uid)):
                return
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
            await e.edit(_menu_text(e.sender_id),
                         buttons=_menu_buttons(e.sender_id),
                         parse_mode="html")

        @c.on(events.CallbackQuery(data=b"help_font"))
        async def help_font_cb(e):
            if not _is_owner(e.sender_id):
                return await e.answer("Owner only.", alert=True)
            from ApexSpam.modules import apexfont
            await apexfont._open_menu(e)
