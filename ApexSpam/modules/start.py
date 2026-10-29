from telethon import events, Button
from ApexSpam import HNDLR, CLIENTS

START_BUTTON = [
    [Button.inline("⚡ C O M M A N D S", data="help_back")],
    [Button.inline("📖 About", data="about_btn"),
     Button.inline("🛡️ Status", data="status_btn")],
    [Button.url("📢 Channel", "https://t.me/ApexSpamXSupport"),
     Button.url("💬 Support", "https://t.me/ApexSpamXSupport")],
]


def register():
    for c in CLIENTS:
        @c.on(events.NewMessage(pattern=r"/start(?: |$)"))
        async def start(e):
            if not e.is_private:
                return
            me = await e.client.get_me()
            text = (
                "╭━━━━━━━━━━━━━━━━━━━━╮\n"
                "   ⚡  **A P E X   S P A M   X**  ⚡\n"
                "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
                f"**Hey** [{e.sender.first_name}](tg://user?id={e.sender.id}) 👋\n"
                "_**Welcome to the ultimate raid engine.**_\n\n"
                "╭─〔 **⚡ CAPABILITIES** 〕─╮\n"
                "│  ◈  Unlimited **Raid**\n"
                "│  ◈  Mass **Spam**\n"
                "│  ◈  Mongo **Sudo**\n"
                "│  ◈  24×7 **Uptime**\n"
                "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
                f"**➤ Prefix**   :  `{HNDLR}`\n"
                f"**➤ Bot**      :  @{me.username}\n"
                "**➤ Status**   :  `✅ Online`\n\n"
                "_Tap below to explore_ 👇"
            )
            await e.reply(text, buttons=START_BUTTON, parse_mode="md")

        @c.on(events.CallbackQuery(data=b"about_btn"))
        async def about(e):
            me = await e.client.get_me()
            text = (
                "╭━━━━━━━━━━━━━━━━━━━━╮\n"
                "   ⚡  **A B O U T**  ⚡\n"
                "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
                "◈ **Name**     :  `Apex Spam X`\n"
                f"◈ **Bot**      :  @{me.username}\n"
                f"◈ **Prefix**   :  `{HNDLR}`\n"
                "◈ **Engine**   :  `Telethon`\n"
                "◈ **Database** :  `MongoDB`\n"
                "◈ **Deploy**   :  `Heroku`\n\n"
                "╭─〔 **👑 CREDITS** 〕─╮\n"
                "│  Developer : **@oyevipthoma88**\n"
                "╰━━━━━━━━━━━━━━━━━━━━╯"
            )
            await e.edit(text, buttons=[[Button.inline("« Back", data="start_back")]], parse_mode="md")

        @c.on(events.CallbackQuery(data=b"status_btn"))
        async def status(e):
            import time
            from ApexSpam import START_TIME
            up = int(time.time() - START_TIME)
            h, r = divmod(up, 3600)
            m, s = divmod(r, 60)
            text = (
                "╭━━━━━━━━━━━━━━━━━━━━╮\n"
                "   🛡️  **S T A T U S**  🛡️\n"
                "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
                f"◈ **Uptime**   :  `{h}h {m}m {s}s`\n"
                "◈ **Status**   :  `✅ Online`\n"
                "◈ **Engine**   :  `Healthy`\n"
                "◈ **Clients**  :  `Active`\n\n"
                "_All systems operational._"
            )
            await e.edit(text, buttons=[[Button.inline("« Back", data="start_back")]], parse_mode="md")

        @c.on(events.CallbackQuery(data=b"start_back"))
        async def back(e):
            me = await e.client.get_me()
            text = (
                "╭━━━━━━━━━━━━━━━━━━━━╮\n"
                "   ⚡  **A P E X   S P A M   X**  ⚡\n"
                "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
                "**Welcome back!** 👋\n"
                f"**Prefix** : `{HNDLR}`    **Bot** : @{me.username}"
            )
            await e.edit(text, buttons=START_BUTTON, parse_mode="md")
