"""Apex Spam X — per-user custom commands (Mongo + cache)."""
import logging
import re
import time

from telethon import events

from ApexSpam import HNDLR, CLIENTS
from ApexSpam.ui import header, quote, kv
from models.customcmds import set_cmd, del_cmd, list_cmds, load_all

log = logging.getLogger("ApexSpam.customcmds")

CACHE = {}
LAST = 0.0
NAME_RE = re.compile(r"^[a-zA-Z0-9_]{2,20}$")
MAX_PER_USER = 30

RESERVED = {
    "start", "help", "ping", "alive", "id", "leave", "gcdiag",
    "raid", "sraid", "craid", "qraid", "abuse", "flirt", "hraid",
    "hrraid", "loveraid", "gm", "ga", "gn", "emoji", "spam",
    "addsudo", "delsudo", "sudolist",
    "addadmin", "deladmin", "listadmin",
    "dev", "setname", "setbio", "setbotpic", "setpic", "delpic",
    "setcaption", "font", "axlogs", "axreboot", "reboot",
    "nc", "banall", "unbanall",
    "rraid", "drraid", "stop", "bspam", "shayriraid",
    "setcmd", "delcmd", "mycmds",
}


async def refresh(force=False):
    global CACHE, LAST
    if not force and time.time() - LAST < 20:
        return
    CACHE = await load_all()
    LAST = time.time()
    log.info(f"custom cmds cached: {len(CACHE)}")


def get(uid, cmd):
    return CACHE.get((uid, cmd.lower()))


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=r"^[\.!/]setcmd(?: |$)"))
        async def setcmd(e):
            parts = e.text.split(maxsplit=2)
            if len(parts) < 3:
                return await e.reply(
                    f"{header('setcmd', '⚠️')}\n\n"
                    + quote(f"<code>{HNDLR}setcmd name response</code>"),
                    parse_mode="html",
                )
            name = parts[1].lower()
            if not NAME_RE.match(name):
                return await e.reply("❌ Name 2–20 chars, letters/numbers/_ only.", parse_mode="html")
            if name in RESERVED:
                return await e.reply("❌ Reserved command name.", parse_mode="html")
            existing = await list_cmds(e.sender_id)
            if len(existing) >= MAX_PER_USER and not any(x["cmd"] == name for x in existing):
                return await e.reply(f"❌ Limit {MAX_PER_USER} commands.", parse_mode="html")
            await set_cmd(e.sender_id, name, parts[2][:500])
            await refresh(force=True)
            await e.reply(
                f"{header('command saved', '✅')}\n\n"
                + quote(f"{kv('Name', name)}\n{kv('Owner', e.sender_id)}", expandable=True),
                parse_mode="html",
            )

        @c.on(events.NewMessage(pattern=r"^[\.!/]delcmd(?: |$)"))
        async def delcmd(e):
            parts = e.text.split(maxsplit=1)
            if len(parts) < 2:
                return await e.reply(f"<code>{HNDLR}delcmd name</code>", parse_mode="html")
            name = parts[1].strip().lower()
            ok = await del_cmd(e.sender_id, name)
            await refresh(force=True)
            await e.reply(
                f"{header('command deleted' if ok else 'not found', '🗑️' if ok else 'ℹ️')}\n\n"
                + quote(f"{kv('Name', name)}"),
                parse_mode="html",
            )

        @c.on(events.NewMessage(pattern=r"^[\.!/]mycmds(?: |$)"))
        async def mycmds(e):
            rows = await list_cmds(e.sender_id)
            body = "\n".join(f"◈ <code>{x['cmd']}</code>" for x in rows) or "<i>none</i>"
            await e.reply(
                f"{header('my commands', '🧩')}\n\n"
                + quote(f"<b>Total</b> : <code>{len(rows)}</code>")
                + f"\n\n{body}",
                parse_mode="html",
            )

        @c.on(events.NewMessage(pattern=rf"^[{HNDLR}!/](\w+)(?: |$)"))
        async def trigger(e):
            if e.out:
                return
            cmd = e.pattern_match.group(1).lower()
            if cmd in RESERVED:
                return
            resp = get(e.sender_id, cmd)
            if not resp:
                return
            try:
                await e.reply(resp)
            except Exception:
                pass
