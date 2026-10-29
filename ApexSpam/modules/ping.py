import time
import logging
from telethon import events, Button
from config import CMD_HNDLR, START_TIME, CLIENTS
from models.users import track_user

log = logging.getLogger("ApexSpam.ping")

def _ping_text(lat: float) -> str:
    up = int(time.time() - START_TIME)
    return (
        "**🏓 P O N G !**\n\n"
        f"**⚡ Latency :** `{lat} ms`\n"
        f"**⏱️ Uptime  :** `{up} sec`\n"
        "**🛰️ Status  :** `Online`\n\n"
        "**🤖 Apex Spam X**"
    )

def register():
    pattern = rf"\{CMD_HNDLR}ping(?: |$)"
    for client in CLIENTS:
        @client.on(events.NewMessage(pattern=pattern))
        async def ping_handler(event):
            log.info(f"🎯 PING HIT from {event.sender_id} in chat {event.chat_id}")
            try:
                await track_user(event.sender_id, getattr(event.sender, "username", None))
            except Exception as e:
                log.exception(f"Mongo track_user failed: {e}")
            t0 = time.time()
            msg = await event.reply("🏓 Pinging...")
            lat = round((time.time() - t0) * 1000, 2)
            await msg.edit(
                _ping_text(lat),
                buttons=[[Button.inline("🔄 Refresh", b"ping_ref")]],
                parse_mode="md",
            )

        @client.on(events.CallbackQuery(data=b"ping_ref"))
        async def ping_refresh_cb(event):
            await event.answer("Refreshing...")
            t0 = time.time()
            lat = round((time.time() - t0) * 1000, 2)
            await event.edit(
                _ping_text(lat),
                buttons=[[Button.inline("🔄 Refresh", b"ping_ref")]],
                parse_mode="md",
            )
