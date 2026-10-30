"""Apex Spam X — echo (clean, no auto-join)."""
from telethon import events
from ApexSpam import HNDLR, OWNER_ID, CLIENTS, SUDO_USERS

ECHO = []


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=rf"^[\.!/]echo(?: |$)"))
        async def echo_cmd(event):
            if event.sender_id not in SUDO_USERS:
                return
            if not event.reply_to_msg_id:
                return await event.reply(
                    f"Usage: `{HNDLR}echo` (reply to a user)", parse_mode="md"
                )
            reply_msg = await event.get_reply_message()
            user_id = reply_msg.sender_id
            if user_id == OWNER_ID:
                return await event.reply("» Owner is protected.")
            if user_id in SUDO_USERS:
                return await event.reply("» Sudo user is protected.")
            key = f"{user_id}_{event.chat_id}"
            if key in ECHO:
                return await event.reply("» Echo already active on this user!")
            ECHO.append(key)
            await event.reply("» Echo activated ✅")

        @c.on(events.NewMessage(incoming=True))
        async def echo_listener(event):
            if event.out:
                return
            key = f"{event.sender_id}_{event.chat_id}"
            if key in ECHO:
                try:
                    await event.reply(event.text or ".")
                except Exception:
                    pass
