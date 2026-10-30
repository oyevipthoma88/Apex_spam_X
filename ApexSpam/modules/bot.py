"""Apex Spam X — ping card (error-safe) + reboot."""
import logging
import time

from telethon import events

from ApexSpam import (
    HNDLR, OWNER_ID, START_TIME,
    HEROKU_APP_NAME, HEROKU_API_KEY, CLIENTS,
)
from ApexSpam import botinfo, respond
from ApexSpam.buttons import ib, grid

log = logging.getLogger("ApexSpam.bot")


def _uptime():
    up = int(time.time() - START_TIME)
    d, r = divmod(up, 86400)
    h, r = divmod(r, 3600)
    m, _ = divmod(r, 60)
    return f"{d}d {h}h {m}m" if d else f"{h}h {m}m"


def _sig(rtt):
    if rtt < 150:
        return "🔥", "ɪɴsᴛᴀɴᴛ"
    if rtt < 400:
        return "⚡", "ғᴀsᴛ"
    if rtt < 800:
        return "🟢", "ɢᴏᴏᴅ"
    return "🐢", "sʟᴏᴡ"


def _card(rtt, username):
    e, label = _sig(rtt)
    return (
        "╭━━━━━━━━━━━━━━━━━━━━━╮\n"
        "   ⚡ <b>ᴀ ᴘ ᴇ x  x  s ᴘ ᴀ ᴍ</b> ⚡\n"
        "╰━━━━━━━━━━━━━━━━━━━━━╯\n\n"
        f"🏓 <b>ᴘ ᴏ ɴ ɢ</b>  ·  {e} <b>{label}</b>\n\n"
        f"<blockquote>"
        f"◈ <b>Latency</b>  :  <code>{rtt} ms</code>\n"
        f"◈ <b>Uptime</b>   :  <code>{_uptime()}</code>\n"
        f"◈ <b>Bot</b>      :  <code>@{username}</code>"
        f"</blockquote>\n\n"
        "<i>💫 ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴀᴘᴇx x sᴘᴀᴍ</i>"
    )


def _btns():
    return grid([
        ib("🔄", b"ping:refresh", "primary"),
        ib("📊", b"ping:speed", "success"),
        ib("✖", b"ping:close", "danger"),
    ], 3)


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=r"^[\.!/]ping(?: |$)"))
        async def ping(e):
            try:
                t0 = time.time()
                u = await botinfo.username(e.client)
                rtt = round((time.time() - t0) * 1000, 2)
                await e.reply(_card(rtt, u), buttons=_btns(), parse_mode="html")
            except Exception as ex:
                log.exception(f"ping failed: {ex}")
                try:
                    await e.reply("🏓 pong", parse_mode="html")
                except Exception:
                    pass

        @c.on(events.CallbackQuery(data=b"ping:refresh"))
        async def refresh(e):
            try:
                await respond.ack(e, "⚡")
                t0 = time.time()
                u = await botinfo.username(e.client)
                rtt = round((time.time() - t0) * 1000, 2)
                await respond.edit(e, _card(rtt, u), _btns())
            except Exception as ex:
                log.exception(f"ping refresh: {ex}")

        @c.on(events.CallbackQuery(data=b"ping:speed"))
        async def speed(e):
            try:
                await respond.ack(e, "📊")
                u = await botinfo.username(e.client)
                samples = []
                for _ in range(3):
                    t = time.time()
                    try:
                        await e.client.get_me()
                        samples.append(round((time.time() - t) * 1000, 2))
                    except Exception:
                        pass
                if not samples:
                    return await respond.ack(e, "Failed", True)
                best, worst = min(samples), max(samples)
                avg = round(sum(samples) / len(samples), 2)
                emoji, label = _sig(avg)
                text = (
                    "╭━━━━━━━━━━━━━━━━━━━━━╮\n"
                    "   ⚡ <b>ᴀ ᴘ ᴇ x  x  s ᴘ ᴀ ᴍ</b> ⚡\n"
                    "╰━━━━━━━━━━━━━━━━━━━━━╯\n\n"
                    f"📊 <b>s ᴘ ᴇ ᴇ ᴅ</b>  ·  {emoji} <b>{label}</b>\n\n"
                    f"<blockquote>"
                    f"◈ <b>Best</b>  :  <code>{best} ms</code>\n"
                    f"◈ <b>Avg</b>   :  <code>{avg} ms</code>\n"
                    f"◈ <b>Worst</b> :  <code>{worst} ms</code>"
                    f"</blockquote>"
                )
                await respond.edit(e, text, _btns())
            except Exception as ex:
                log.exception(f"ping speed: {ex}")

        @c.on(events.CallbackQuery(data=b"ping:close"))
        async def close_ping(e):
            try:
                await respond.ack(e)
                await e.delete()
            except Exception:
                pass

        @c.on(events.NewMessage(pattern=r"^[\.!/]reboot(?: |$)"))
        async def reboot(e):
            if e.sender_id != OWNER_ID:
                return
            if not HEROKU_APP_NAME or not HEROKU_API_KEY:
                return await e.reply("⚠️ Not configured.", parse_mode="html")
            try:
                import heroku3
                app = heroku3.from_key(HEROKU_API_KEY).app(HEROKU_APP_NAME)
                await e.reply("♻️ Restarting…", parse_mode="html")
                app.restart()
            except Exception as err:
                await e.reply(f"❌ <code>{err}</code>", parse_mode="html")
