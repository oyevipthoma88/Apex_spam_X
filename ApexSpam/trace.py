"""Apex Spam X — deep audit log to LOG_CHANNEL_ID."""
import html
import logging
import time

from telethon import events

from ApexSpam import cache

try:
    from ApexSpam import LOG_CHANNEL_ID
except Exception:
    LOG_CHANNEL_ID = 0

try:
    from ApexSpam import CLIENTS
except Exception:
    CLIENTS = []

log = logging.getLogger("ApexSpam.trace")
_client = None


def _ts():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())


def _u(uid, name):
    try:
        safe_name = html.escape(str(name or "User"))
        return (
            f'<a href="tg://user?id={int(uid)}">{safe_name}</a> '
            f'<code>{int(uid)}</code>'
        )
    except Exception:
        return f"<code>{uid}</code>"


def _claim(*key):
    ck = ("trace",) + key
    if cache.get(ck):
        return False
    cache.set(ck, True, 60)
    return True


async def _send(text):
    if not LOG_CHANNEL_ID or _client is None:
        return
    try:
        await _client.send_message(
            LOG_CHANNEL_ID, text, parse_mode="html", link_preview=False
        )
    except Exception as e:
        log.debug(f"trace send: {e}")


def _card(icon, title, rows):
    body = "\n".join(f"◈ <b>{k}</b> : {v}" for k, v in rows)
    return f"{icon} <b>{title}</b>\n\n<blockquote>{body}</blockquote>"


async def log_command(user_id, user_name, chat_id, chat_title, text,
                      is_private, bot_username):
    where = (
        "📩 DM" if is_private
        else f"👥 <b>{html.escape(str(chat_title))}</b> <code>{chat_id}</code>"
    )
    await _send(_card("⚡", "COMMAND", [
        ("Time", f"<code>{_ts()}</code>"),
        ("Bot", f"<code>@{bot_username}</code>"),
        ("User", _u(user_id, user_name)),
        ("Where", where),
        ("Cmd", f"<code>{html.escape(text[:200])}</code>"),
    ]))


async def log_button(user_id, user_name, chat_id, chat_title, data, bot_username):
    await _send(_card("🖱️", "BUTTON", [
        ("Time", f"<code>{_ts()}</code>"),
        ("Bot", f"<code>@{bot_username}</code>"),
        ("User", _u(user_id, user_name)),
        ("Chat", f"<b>{html.escape(str(chat_title))}</b> <code>{chat_id}</code>"),
        ("Data", f"<code>{html.escape(data)}</code>"),
    ]))


async def log_start(user_id, user_name, bot_username, is_private):
    await _send(_card("🚀", "/START", [
        ("Time", f"<code>{_ts()}</code>"),
        ("Bot", f"<code>@{bot_username}</code>"),
        ("User", _u(user_id, user_name)),
        ("Via", "📩 DM" if is_private else "👥 Group"),
    ]))


async def log_new_chat(chat_id, chat_title, is_private, bot_username,
                       sender_id, sender_name):
    if is_private:
        await _send(_card("🆕", "NEW DM", [
            ("Time", f"<code>{_ts()}</code>"),
            ("Bot", f"<code>@{bot_username}</code>"),
            ("User", _u(sender_id, sender_name)),
        ]))
    else:
        await _send(_card("🆕", "NEW GROUP", [
            ("Time", f"<code>{_ts()}</code>"),
            ("Bot", f"<code>@{bot_username}</code>"),
            ("Group", f"<b>{html.escape(str(chat_title))}</b> <code>{chat_id}</code>"),
            ("First msg", _u(sender_id, sender_name)),
        ]))


async def log_sudo(action, actor_id, actor_name, target_id, target_name="?"):
    await _send(_card("🛡️", f"SUDO {action.upper()}", [
        ("Time", f"<code>{_ts()}</code>"),
        ("By", _u(actor_id, actor_name)),
        ("Target", _u(target_id, target_name)),
    ]))


async def log_admin(action, actor_id, actor_name, target_id):
    await _send(_card("👤", f"ADMIN {action.upper()}", [
        ("Time", f"<code>{_ts()}</code>"),
        ("By", _u(actor_id, actor_name)),
        ("Target", f"<code>{target_id}</code>"),
    ]))


async def log_gc(action, actor_id, actor_name, chat_id, chat_title="?"):
    await _send(_card("📌", f"GC {action.upper()}", [
        ("Time", f"<code>{_ts()}</code>"),
        ("By", _u(actor_id, actor_name)),
        ("Group", f"<b>{html.escape(str(chat_title))}</b> <code>{chat_id}</code>"),
    ]))


async def log_owner(action, actor_id, actor_name, field, value):
    await _send(_card("👑", f"OWNER {action.upper()}", [
        ("Time", f"<code>{_ts()}</code>"),
        ("By", _u(actor_id, actor_name)),
        ("Field", f"<code>{field}</code>"),
        ("Value", f"<code>{html.escape(str(value)[:80])}</code>"),
    ]))


async def log_raid(actor_id, actor_name, target_id, target_name,
                   chat_id, chat_title, cmd, count):
    await _send(_card("⚔️", "RAID", [
        ("Time", f"<code>{_ts()}</code>"),
        ("Cmd", f"<code>{cmd}</code>"),
        ("By", _u(actor_id, actor_name)),
        ("Target", _u(target_id, target_name)),
        ("Chat", f"<b>{html.escape(str(chat_title))}</b> <code>{chat_id}</code>"),
        ("Count", f"<code>{count}</code>"),
    ]))


async def _who(e):
    name = "User"
    title = "DM" if getattr(e, "is_private", False) else "?"
    try:
        s = await e.get_sender()
        name = getattr(s, "first_name", "") or "User"
    except Exception:
        pass
    try:
        ch = await e.get_chat()
        if not getattr(e, "is_private", False):
            title = getattr(ch, "title", "?") or "?"
    except Exception:
        pass
    return name, title


def register():
    global _client
    if not LOG_CHANNEL_ID:
        log.warning("LOG_CHANNEL_ID not set — trace disabled")
        return
    if not CLIENTS:
        return
    _client = CLIENTS[0]

    for c in CLIENTS:
        @c.on(events.NewMessage())
        async def on_msg(e):
            if e.out:
                return
            try:
                me = await e.client.get_me()
                uname = me.username or "bot"
            except Exception:
                return
            try:
                name, title = await _who(e)
                try:
                    from models.chatlog import mark_seen
                    if await mark_seen(e.chat_id, title, e.is_private, uname):
                        await log_new_chat(
                            e.chat_id, title, e.is_private, uname,
                            e.sender_id, name,
                        )
                except Exception:
                    pass
                txt = e.text or ""
                if txt and txt[0] in ".!/":
                    if _claim("cmd", e.chat_id, e.id):
                        await log_command(
                            e.sender_id, name, e.chat_id, title,
                            txt, e.is_private, uname,
                        )
            except Exception as ex:
                log.debug(f"trace on_msg: {ex}")

        @c.on(events.CallbackQuery())
        async def on_btn(e):
            try:
                me = await e.client.get_me()
                uname = me.username or "bot"
                name, title = await _who(e)
                data = e.data.decode(errors="ignore") if e.data else "?"
                if _claim("btn", e.chat_id, e.id, data):
                    await log_button(
                        e.sender_id, name, e.chat_id, title, data, uname,
                    )
            except Exception as ex:
                log.debug(f"trace on_btn: {ex}")

    log.info("✅ trace registered")
