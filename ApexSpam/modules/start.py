from telethon import events, Button
from config import CLIENTS, CMD_HNDLR

START_BUTTON = [
    [Button.inline("📖 Help", data="help_back")],
    [Button.url("📢 Support", "https://t.me/YourSupportChannel")],
]


def register():
    for client in CLIENTS:
        @client.on(events.NewMessage(pattern=r"/start(?: |$)"))
        async def start_handler(event):
            if not event.is_private:
                return
            me = await event.client.get_me()
            text = (
                f"**👋 Hello {event.sender.first_name}!**\n\n"
                f"I am **{me.first_name}** — a powerful spam bot.\n"
                f"**Prefix:** `{CMD_HNDLR}`\n"
                f"**Commands:** `{CMD_HNDLR}help`\n\n"
                "**⚡ Apex Spam X**"
            )
            await event.reply(text, buttons=START_BUTTON, parse_mode="md")
