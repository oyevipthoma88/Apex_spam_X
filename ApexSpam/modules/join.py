from telethon import events
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from config import CLIENTS, CMD_HNDLR
from ApexSpam.patterns import cmd
from ApexSpam.modules._helpers import has_perm

def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=cmd("join")))
        async def join(e):
            if not await has_perm(e):
                return
            parts = e.text.split(maxsplit=1)
            if len(parts) < 2:
                return await e.reply(f"Usage: `{CMD_HNDLR}join <link>`", parse_mode="md")
            link = parts[1].strip()
            try:
                if "+" in link or "joinchat" in link:
                    hash_ = link.split("+")[-1].split("/")[-1]
                    await e.client(ImportChatInviteRequest(hash_))
                else:
                    await e.client(JoinChannelRequest(link))
                await e.reply("✅ Joined.")
            except Exception as err:
                await e.reply(f"❌ {err}")
