"""Apex Spam X — clean /start with compact buttons."""
import logging
import time
from io import BytesIO

from telethon import events

from ApexSpam import (
    HNDLR, START_TIME, CLIENTS, OWNER_ID,
    SUPPORT_LINK, OWNER_USERNAME, SUDO_GC_LINK, UPDATE_LINK,
)
from ApexSpam.ui import header, quote, divider, link_user, footer, safe_format
from ApexSpam.buttons import ib, ub
from models.bot_settings import get_value

log = logging.getLogger("ApexSpam.start")

DEFAULT_CAPTION = "{header}\n\n{greet}\n\n{q1}\n\n{q2}\n\n{meta}"


def _buttons(uid=0):
    rows = [
        [ib("⚡ C O M M A N D S", b"help_back", "primary"),
         ib("🎓 Tutorial", b"tutorial_btn", "success")],
    ]
    row = []
    if SUDO_GC_LINK:
        row.append(ub("📢 Sudo GC", SUDO_GC_LINK, "primary"))
    if UPDATE_LINK:
        row.append(ub("🚀 Update", UPDATE_LINK, "primary"))
    if row:
        rows.append(row)
    row = []
    if OWNER_USERNAME:
        row.append(ub("👤 Owner", f"https://t.me/{OWNER_USERNAME}", "primary"))
    elif OWNER_ID:
        row.append(ub("👤 Owner", f"tg://user?id={OWNER_ID}", "primary"))
    if SUPPORT_LINK:
        row.append(ub("💬 Support", SUPPORT_LINK, "primary"))
    if row:
        rows.append(row)
    if uid == OWNER_ID:
        rows.append([ib("👑 Owner Panel", b"owner_panel", "danger")])
    return rows


async def _build(e, bot_username):
    up = int(time.time() - START_TIME)
    h, r = divmod(up, 3600)
    m, s = divmod(r, 60)
    try:
        tpl = await get_value("start_caption")
    except Exception:
        tpl = None
    text = safe_format(
        tpl if isinstance(tpl, str) and tpl.strip() else DEFAULT_CAPTION,
        header=header("apex spam x", "⚡"),
        greet=f"Hey {link_user(e.sender_id, e.sender.first_name or 'User')} 👋",
        q1=quote("<i>Your ultimate raid companion.</i>"),
        q2=quote(
            f"◈ <b>Prefix</b> : <code>{HNDLR}</code>  •  <code>!</code>  •  <code>/</code>\n"
            f"◈ <b>Bot</b>    : <code>@{bot_username}</code>\n"
            f"◈ <b>Uptime</b> : <code>{h}h {m}m {s}s</code>"
        ),
        meta=f"{divider()}\n<i>Tap a button below</i> 👇",
    )
    return text.strip() or "⚡ <b>Apex Spam X</b> — online"


async def _send(e, text):
    try:
        pic = await get_value("start_pic")
        ext = await get_value("start_pic_ext") or "jpg"
        if pic:
            stream = BytesIO(bytes(pic))
            stream.name = f"apex_start.{ext}"
            await e.reply(text, file=stream, buttons=_buttons(e.sender_id),
                          parse_mode="html")
            return
    except Exception as ex:
        log.warning(f"start pic failed: {ex}")
    try:
        await e.reply(text, buttons=_buttons(e.sender_id), parse_mode="html")
    except Exception as ex:
        log.exception(f"start text failed: {ex}")


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=rf"^[{HNDLR}!/]start(?:@\w+)?(?:\s|$)"))
        async def start(e):
            try:
                me = await e.client.get_me()
                username = me.username or "bot"
            except Exception:
                username = "bot"
            if not e.is_private:
                try:
                    await e.reply(f"👋 DM me to start — @{username}")
                except Exception:
                    pass
                return
            try:
                await _send(e, await _build(e, username))
            except Exception as ex:
                log.exception(f"start failed: {ex}")

        @c.on(events.CallbackQuery(data=b"tutorial_btn"))
        async def tutorial(e):
            try:
                text = (
                    f"{header('tutorial', '🎓')}\n\n"
                    + quote(
                        f"<b>① Prefix</b>\n"
                        f"Type <code>{HNDLR}</code> <code>!</code> <code>/</code> before any command.\n\n"
                        f"<b>② Help</b>\n"
                        f"<code>{HNDLR}help</code> — categories\n\n"
                        f"<b>③ Raid</b>\n"
                        f"<code>{HNDLR}raid 5 @user</code>\n"
                        f"<code>{HNDLR}raid 5</code> (reply to target)\n"
                        f"<code>{HNDLR}rraid 3</code> — auto-fire on their next msg\n"
                        f"<code>{HNDLR}stop</code> — abort\n\n"
                        f"<b>④ Font</b>\n"
                        f"<code>{HNDLR}font</code> — style all raid data\n\n"
                        f"<b>⑤ Custom commands</b>\n"
                        f"<code>{HNDLR}setcmd hi Hello!</code> → <code>{HNDLR}hi</code>\n"
                        f"<code>{HNDLR}mycmds</code> / <code>{HNDLR}delcmd hi</code>",
                        expandable=True,
                    )
                    + f"\n{footer()}"
                )
                await e.edit(text,
                             buttons=[[ib("« Back", b"start_back", "primary")]],
                             parse_mode="html")
            except Exception:
                pass

        @c.on(events.CallbackQuery(data=b"start_back"))
        async def back(e):
            try:
                me = await e.client.get_me()
                await e.edit(await _build(e, me.username or "bot"),
                             buttons=_buttons(e.sender_id),
                             parse_mode="html")
            except Exception:
                pass

        # legacy callbacks (keep to avoid dead buttons)
        @c.on(events.CallbackQuery(data=b"about_btn"))
        @c.on(events.CallbackQuery(data=b"status_btn"))
        async def legacy(e):
            try:
                me = await e.client.get_me()
                await e.edit(
                    f"{header('about', '⚡')}\n\n"
                    + quote(
                        f"◈ <b>Bot</b>   : <code>@{me.username}</code>\n"
                        f"◈ <b>Prefix</b>: <code>{HNDLR}</code>"
                    )
                    + f"\n{footer()}",
                    buttons=[[ib("« Back", b"start_back", "primary")]],
                    parse_mode="html",
                )
            except Exception:
                pass
