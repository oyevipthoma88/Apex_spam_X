from telethon import events
from ApexSpam import HNDLR, OWNER_ID, CLIENTS, SUDO_USERS
from ApexSpam.dedup import is_dup
from ApexSpam.ui import header, quote, divider, footer
from ApexSpam.buttons import ib


def _owner(uid): return uid == OWNER_ID
def _sudo(uid):  return uid in SUDO_USERS or _owner(uid)


def _menu_text(uid):
    role = "👑 Owner" if _owner(uid) else ("🛡️ Sudo" if uid in SUDO_USERS else "👤 User")
    return (
        f"{header('apex help', '⚡')}\n\n"
        + quote(f"◈ <b>Prefix</b>  :  <code>{HNDLR}</code>\n◈ <b>Role</b>    :  <b>{role}</b>")
        + f"\n\n{divider()}\n<i>Select a category</i> 👇\n{footer()}"
    )


def _menu_buttons(uid):
    rows = []
    if _sudo(uid):
        rows.append([ib("🔫 Raid", b"help_raid", "primary"), ib("💬 Spam", b"help_spam", "primary")])
    rows.append([ib("🛠️ Extra", b"help_extra", "primary")])
    if _owner(uid):
        rows.append([ib("🛡️ Admin", b"help_admin", "danger"), ib("⚔️ Moderation", b"help_mod", "danger")])
        rows.append([ib("🔐 Sudo", b"help_sudo", "success"), ib("🎨 Font", b"help_font", "success")])
    return rows


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
        f"<code>{HNDLR}ping</code>     — live latency\n"
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
    "help_mod": header("moderation", "⚔️") + "\n\n" + quote(
        f"<code>{HNDLR}banall</code>      — ban all members\n"
        f"<code>{HNDLR}unbanall</code>    — unban all\n"
        f"<code>{HNDLR}nc [limit]</code>  — nuke chat\n"
        f"<code>{HNDLR}kick</code>        — kick (reply)\n"
        f"<code>{HNDLR}ban</code>         — ban (reply)",
        expandable=True,
    ) + "\n\n" + quote(
        "<b>Perm</b> : <code>Owner / Sudo</code>\n"
        "<b>Need</b> : bot admin + ban/delete rights\n"
        "<i>All destructive actions ask for confirmation.</i>"
    ),
    "help_sudo": header("sudo", "🔐") + "\n\n" + quote(
        f"<code>{HNDLR}addsudo ID</code>\n"
        f"<code>{HNDLR}delsudo ID</code>\n"
        f"<code>{HNDLR}listsudo</code>",
        expandable=True,
    ) + "\n\n" + quote("<i>Mongo + env union — global.</i>"),
    "help_font": header("font", "🎨") + "\n\n" + quote(
        f"<code>{HNDLR}font</code>        — studio\n"
        f"<code>{HNDLR}font bold</code>   — by name\n"
        f"<code>{HNDLR}font 1</code>      — by index\n\n"
        "Applies to raids, spam and every bot reply.",
        expandable=True,
    ) + "\n\n" + quote("<b>Perm</b> : <code>Owner only</code>"),
}

_GATE_OWNER = {"help_admin", "help_sudo", "help_font"}
_GATE_SUDO = {"help_raid", "help_spam", "help_mod"}


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=rf"^[\.!/]help(?: |$)"))
        async def help_cmd(e):
            if is_dup(e.chat_id, e.id):
                return
            await e.reply(_menu_text(e.sender_id), buttons=_menu_buttons(e.sender_id), parse_mode="html")

        @c.on(events.NewMessage(pattern=rf"^[\.!/]help (\w+)(?: |$)"))
        async def help_text(e):
            key = f"help_{e.pattern_match.group(1).lower()}"
            uid = e.sender_id
            if key in _GATE_OWNER and not _owner(uid): return
            if key in _GATE_SUDO and not _sudo(uid): return
            if key in PAGES:
                await e.reply(PAGES[key], parse_mode="html")

        def _mk(txt):
            async def cb(e):
                await e.edit(txt, buttons=[[ib("« Back", b"help_back", "primary")]], parse_mode="html")
            return cb

        for key, txt in PAGES.items():
            c.on(events.CallbackQuery(data=key.encode()))(_mk(txt))

        @c.on(events.CallbackQuery(data=b"help_back"))
        async def back(e):
            await e.edit(_menu_text(e.sender_id), buttons=_menu_buttons(e.sender_id), parse_mode="html")

        @c.on(events.CallbackQuery(data=b"help_font"))
        async def help_font(e):
            if not _owner(e.sender_id):
                return await e.answer("Owner only.", alert=True)
            from ApexSpam.modules.apexfont import _open_menu
            await _open_menu(e)
