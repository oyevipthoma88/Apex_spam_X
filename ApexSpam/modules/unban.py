from telethon import events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from config import CLIENTS, CMD_HNDLR
from ApexSpam.patterns import cmd
from ApexSpam.modules._helpers import has_perm, resolve_user

def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=cmd("unban")))
        async def unban(e):
            if not await has_perm(e):
                return
            if not (e.is_group or e.is_channel):
                return await e.reply("Groups only.")
            parts = e.text.split(maxsplit=1)
            uid = await resolve_user(e, parts[1] if len(parts) > 1 else "")
            if not uid:
                return await e.reply(f"Usage: `{CMD_HNDLR}unban <user|reply>`", parse_mode="md")
            try:
                await e.client(EditBannedRequest(e.chat_id, uid, ChatBannedRights(until_date=None)))
                await e.reply(f"✅ Unbanned `{uid}`", parse_mode="md")
            except Exception as err:
                await e.reply(f"❌ {err}")
