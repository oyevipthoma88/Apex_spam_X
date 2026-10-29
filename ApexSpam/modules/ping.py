import time
from telethon import events, Button
from config import START_TIME, CLIENTS
from ApexSpam.patterns import cmd
from models.users import track_user


def _text(lat: float) -> str:
    up = int(time.time() - START_TIME)
    return (
        "**🏓 P O N G !**\n\n"
        f"**⚡ Latency :** `{lat} ms`\n"
        f"**⏱️ Uptime  :** `{up} sec`\n"
        "**🛰️ Status  :** `Online`\n\n"
        "**🤖 Apex Spam X**"
    )


def register():
    for client in CLIENTS:
        @client.on(events.NewMessage(pattern=cmd("ping"), incoming=True))
        async def ping_handler(event):
            t0 = time.time()
            msg = await event.reply("🏓 Pinging...")
            lat = round((time.time() - t0) * 1000, 2)
            await msg.edit(
                _text(lat),
                buttons=[[Button.inline("🔄 Refresh", b"ping_ref")]],
                parse_mode="md",
            )
            try:
                await track_user(event.sender_id, getattr(event.sender, "username", None))
            except Exception:
                pass

        @client.on(events.CallbackQuery(data=b"ping_ref"))
        async def ping_refresh_cb(event):
            await event.answer("Refreshing...")
            t0 = time.time()
            lat = round((time.time() - t0) * 1000, 2)
            await event.edit(
                _text(lat),
                buttons=[[Button.inline("🔄 Refresh", b"ping_ref")]],
                parse_mode="md",
            )
