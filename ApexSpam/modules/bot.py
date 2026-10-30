"""Apex Spam X — premium ping card with styled font + speed test."""
import time

from telethon import events

from ApexSpam import (
    HNDLR, OWNER_ID, START_TIME,
    HEROKU_APP_NAME, HEROKU_API_KEY, CLIENTS,
)
from ApexSpam import botinfo, respond, gcguard
from ApexSpam.buttons import ib, grid
from ApexSpam.ui import bread, quote, kv


# rtt limit, emoji, label, bar count
_TIERS = [
    (100,   "🔥", "Lightning", 10),
    (250,   "⚡", "Excellent",  9),
    (500,   "🟢", "Good",       7),
    (800,   "🟡", "Fair",       5),
    (99999, "🔴", "Slow",       3),
]

_QUALITY = {
    "Lightning": "🚀 𝘓 𝘪 𝘨 𝘩 𝘵 𝘯 𝘪 𝘯 𝘨",
    "Excellent": "✨ 𝘌 𝘹 𝘤 𝘦 𝘭 𝘭 𝘦 𝘯 𝘵",
    "Good":      "👍 𝘎 𝘰 𝘰 𝘥",
    "Fair":      "😐 𝘍 𝘢 𝘪 𝘳",
    "Slow":      "🐢 𝘚 𝘭 𝘰 𝘸",
}


def _uptime():
    up = int(time.time() - START_TIME)
    d, r = divmod(up, 86400)
    h, r = divmod(r, 3600)
    m, s = divmod(r, 60)
    if d:
        return f"{d}d {h}h {m}m"
    return f"{h}h {m}m {s}s"


def _tier(rtt):
    for lim, emoji, label, filled in _TIERS:
        if rtt < lim:
            return emoji, label, filled
    return "🔴", "Slow", 3


def _card(rtt, username):
    emoji, label, filled = _tier(rtt)
    pct = filled * 10
    bar = "▰" * filled + "▱" * (10 - filled)
    quality = _QUALITY.get(label, "")

    return (
        "╭━━━━━━━━━━━━━━━━━━━━━╮\n"
        "   ⚡ <b>ᴀ ᴘ ᴇ x   s ᴘ ᴀ ᴍ   x</b> ⚡\n"
        "╰━━━━━━━━━━━━━━━━━━━━━╯\n\n"
        "       🏓 <b>ᴘ ᴏ ɴ ɢ !</b>\n\n"
        "<blockquote>"
        f" {emoji} <b>Signal</b>  ➤  {quality}\n"
        f" ⚡ <b>Latency</b> ➤  <code>{rtt} ms</code>\n"
        f" ⏱️ <b>Uptime</b>  ➤  <code>{_uptime()}</code>\n"
        f" 🤖 <b>Bot</b>     ➤  <code>@{username}</code>"
        "</blockquote>\n\n"
        f"<code>{bar}</code>  <b>{pct}%</b>\n\n"
        "<i>💫 𝘍 𝘢 𝘴 𝘵 • 𝘚 𝘵 𝘢 𝘣 𝘭 𝘦 • 𝘖 𝘯 𝘭 𝘪 𝘯 𝘦</i>"
    )


async def _gc_warning(client, chat_id):
    """Return warning text if bot is not admin in GC, else ''."""
    try:
        me = await client.get_me()
        perms = await client.get_permissions(chat_id, me.id)
        if not getattr(perms, "is_admin", False):
            return (
                "\n\n<blockquote>⚠️ <b>Bot is not admin</b>\n"
                "Run <code>.gcsetup</code> for fix.</blockquote>"
            )
    except Exception:
        pass
    return ""


def _btns():
    return grid([
        ib("🔄 Refresh", b"ping:refresh", "primary"),
        ib("📊 Speed Test", b"ping:speed", "success"),
        ib("✖ Close", b"ping:close", "danger"),
    ], 2)


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=r"^[\.!/]ping(?: |$)"))
        async def ping(e):
            t0 = time.time()
            u = await botinfo.username(e.client)
            rtt = round((time.time() - t0) * 1000, 2)
            card = _card(rtt, u)
            if not e.is_private:
                card += await gcguard.warn_if_not_admin(e.client, e.chat_id, e.is_private)
            await e.reply(card, buttons=_btns(), parse_mode="html")

        @c.on(events.CallbackQuery(data=b"ping:refresh"))
        async def refresh(e):
            await respond.ack(e, "⚡ Refreshing…")
            t0 = time.time()
            u = await botinfo.username(e.client)
            rtt = round((time.time() - t0) * 1000, 2)
            await respond.edit(e, _card(rtt, u), _btns())

        @c.on(events.CallbackQuery(data=b"ping:speed"))
        async def speed(e):
            await respond.ack(e, "🏃 Running 3 tests…")
            u = await botinfo.username(e.client)
            samples = []
            for _ in range(3):
                t0 = time.time()
                try:
                    await e.client.get_me()
                    samples.append(round((time.time() - t0) * 1000, 2))
                except Exception:
                    pass
            if not samples:
                return await respond.edit(e, "❌ Speed test failed.", _btns())
            best = min(samples)
            worst = max(samples)
            avg = round(sum(samples) / len(samples), 2)
            emoji, label, filled = _tier(avg)
            bar = "▰" * filled + "▱" * (10 - filled)
            text = (
                "╭━━━━━━━━━━━━━━━━━━━━━╮\n"
                "   📊 <b>s ᴘ ᴇ ᴇ ᴅ   ᴛ ᴇ s ᴛ</b> 📊\n"
                "╰━━━━━━━━━━━━━━━━━━━━━╯\n\n"
                "<blockquote>"
                f" 🚀 <b>Best</b>    ➤  <code>{best} ms</code>\n"
                f" 📊 <b>Average</b> ➤  <code>{avg} ms</code>\n"
                f" 🐢 <b>Worst</b>   ➤  <code>{worst} ms</code>\n"
                f" {emoji} <b>Rating</b>  ➤  <b>{label}</b>\n"
                f" 🤖 <b>Bot</b>     ➤  <code>@{u}</code>"
                "</blockquote>\n\n"
                f"<code>{bar}</code>  <b>{filled * 10}%</b>\n\n"
                "<i>💫 3 samples averaged</i>"
            )
            await respond.edit(e, text, _btns())

        @c.on(events.CallbackQuery(data=b"ping:close"))
        async def close_ping(e):
            await respond.ack(e)
            try:
                await e.delete()
            except Exception:
                pass

        @c.on(events.NewMessage(pattern=r"^[\.!/]reboot(?: |$)"))
        async def reboot(e):
            if e.sender_id != OWNER_ID:
                return
            if not HEROKU_APP_NAME or not HEROKU_API_KEY:
                return await e.reply("⚠️ Reboot not configured.", parse_mode="html")
            try:
                import heroku3
                app = heroku3.from_key(HEROKU_API_KEY).app(HEROKU_APP_NAME)
                await e.reply("♻️ Restarting…", parse_mode="html")
                app.restart()
            except Exception as err:
                await e.reply(f"❌ <code>{err}</code>", parse_mode="html")
