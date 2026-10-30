"""Apex Spam X — alive card (no external URLs)."""
import time

from telethon import events

from ApexSpam import HNDLR, START_TIME, CLIENTS
from ApexSpam.ui import title, quote, kv, footer
from ApexSpam.buttons import ib, grid


def _card(username):
    up = int(time.time() - START_TIME)
    h, r = divmod(up, 3600)
    m, s = divmod(r, 60)
    return (
        f"{title('a l i v e', '💠')}\n"
        + quote(
            f"{kv('Bot', '@' + username)}\n"
            f"{kv('Uptime', f'{h}h {m}m {s}s')}\n"
            f"{kv('Status', '✅ Online')}"
        )
        + f"\n{footer()}"
    )


def _btns():
    return grid([
        ib("📊 Stats", b"ax_stats", "primary"),
        ib("✖ Close", b"ax_close", "danger"),
    ], 2)


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=r"^[\.!/]alive(?: |$)"))
        async def alive(e):
            me = await e.client.get_me()
            await e.reply(_card(me.username or "bot"),
                          buttons=_btns(), parse_mode="html")

        @c.on(events.CallbackQuery(data=b"ax_stats"))
        async def ax_stats(e):
            up = int(time.time() - START_TIME)
            h, r = divmod(up, 3600)
            m, s = divmod(r, 60)
            text = (
                f"{title('s t a t s', '📊')}\n"
                + quote(
                    f"{kv('Uptime', f'{h}h {m}m {s}s')}\n"
                    f"{kv('Clients', len(CLIENTS))}\n"
                    f"{kv('Prefix', HNDLR)}"
                )
                + f"\n{footer()}"
            )
            await e.edit(text,
                         buttons=[[ib("« Back", b"ax_back", "primary")]],
                         parse_mode="html")

        @c.on(events.CallbackQuery(data=b"ax_back"))
        async def ax_back(e):
            me = await e.client.get_me()
            await e.edit(_card(me.username or "bot"),
                         buttons=_btns(), parse_mode="html")

        @c.on(events.CallbackQuery(data=b"ax_close"))
        async def ax_close(e):
            try:
                await e.delete()
            except Exception:
                pass
