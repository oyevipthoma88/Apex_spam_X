"""Apex Spam X — full message logger + .diag command."""
import logging

from telethon import events

from ApexSpam import HNDLR, OWNER_ID, CLIENTS
from ApexSpam import state
from ApexSpam.ui import title, quote, kv

log = logging.getLogger("ApexSpam.debug")


def register():
    for c in CLIENTS:
        # ── EVERY incoming message gets logged ──
        @c.on(events.NewMessage(incoming=True))
        async def log_all(e):
            try:
                t = (e.text or "")
                log.info(
                    f"MSG uid={e.sender_id} chat={e.chat_id} "
                    f"priv={e.is_private} text={t[:70]!r}"
                )
            except Exception as ex:
                log.exception(f"log_all failed: {ex}")

        # ── .diag — module load status ──
        @c.on(events.NewMessage(pattern=rf"^[\.!/]diag(?: |$)"))
        async def diag(e):
            if e.sender_id != OWNER_ID:
                return
            mods = dict(state.LOADED)
            ok = [k for k, v in mods.items() if v == "OK"]
            bad = [(k, v) for k, v in mods.items() if v != "OK"]

            body = f"<b>OK</b>  :  <code>{len(ok)}</code>\n<b>FAIL</b>  :  <code>{len(bad)}</code>\n\n"
            if bad:
                body += "<b>FAILURES</b>\n"
                for k, v in bad:
                    body += f"❌ <code>{k}</code>\n   <i>{str(v)[:120]}</i>\n"
            if not mods:
                body = "<i>state.LOADED empty — main.py patch missing</i>"

            text = f"{title('d i a g', '🩺')}\n" + quote(body, expandable=True)
            await e.reply(text, parse_mode="html")
