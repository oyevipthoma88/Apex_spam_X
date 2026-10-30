"""Apex Spam X — log channel + structured event logs."""
import logging
from datetime import datetime

from ApexSpam import LOG_CHANNEL_ID

log = logging.getLogger("ApexSpam.event")
_client = None


def set_client(c):
    global _client
    _client = c


async def _send(text):
    if not LOG_CHANNEL_ID or _client is None:
        return
    try:
        await _client.send_message(LOG_CHANNEL_ID, text, parse_mode="html")
    except Exception as e:
        log.warning(f"log channel send failed: {e}")


def _ts():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


def _u(uid, name):
    return f"<a href='tg://user?id={uid}'>{name}</a> <code>{uid}</code>"


async def log_raid(user_id, user_name, target_id, target_name,
                   chat_id, chat_title, cmd, count):
    text = (
        "<b>⚔️ RAID EXECUTED</b>\n"
        f"◈ <b>Time</b>   : <code>{_ts()}</code>\n"
        f"◈ <b>Cmd</b>    : <code>{cmd}</code>\n"
        f"◈ <b>By</b>     : {_u(user_id, user_name)}\n"
        f"◈ <b>Target</b> : {_u(target_id, target_name)}\n"
        f"◈ <b>Chat</b>   : <b>{chat_title}</b> <code>{chat_id}</code>\n"
        f"◈ <b>Count</b>  : <code>{count}</code>"
    )
    await _send(text)
    log.info(f"RAID cmd={cmd} by={user_id} -> {target_id} @{chat_id} n={count}")


async def log_spam(user_id, user_name, chat_id, chat_title, count, preview):
    text = (
        "<b>💬 SPAM EXECUTED</b>\n"
        f"◈ <b>Time</b>   : <code>{_ts()}</code>\n"
        f"◈ <b>By</b>     : {_u(user_id, user_name)}\n"
        f"◈ <b>Chat</b>   : <b>{chat_title}</b> <code>{chat_id}</code>\n"
        f"◈ <b>Count</b>  : <code>{count}</code>\n"
        f"◈ <b>Text</b>   : <code>{preview[:100]}</code>"
    )
    await _send(text)
    log.info(f"SPAM by={user_id} @{chat_id} n={count} text={preview[:40]!r}")


async def log_bot(action, username, detail=""):
    text = (
        "<b>🤖 BOT EVENT</b>\n"
        f"◈ <b>Time</b>   : <code>{_ts()}</code>\n"
        f"◈ <b>Action</b> : <code>{action}</code>\n"
        f"◈ <b>Bot</b>    : @{username}\n"
        f"◈ <b>Detail</b> : <code>{detail}</code>"
    )
    await _send(text)
    log.info(f"BOT {action} @{username} {detail}")


async def log_command(user_id, user_name, chat_id, chat_title, cmd):
    log.info(f"CMD {cmd} by={user_id} @{chat_id}")
