import time
from telethon import events
from ApexSpam import HNDLR, START_TIME, X1, X2, X3, X4, X5, X6, X7, X8, X9, X10


def register():
    for c in [X1, X2, X3, X4, X5, X6, X7, X8, X9, X10]:
        @c.on(events.NewMessage(pattern=rf"^[\.!/]apxping(?: |$)"))
        async def apxping(e):
            t0 = time.time()
            msg = await e.reply("⚡ `Pinging...`", parse_mode="md")
            lat = round((time.time() - t0) * 1000, 2)
            up = int(time.time() - START_TIME)
            h, r = divmod(up, 3600)
            m, s = divmod(r, 60)
            text = (
                "╭━━━━━━━━━━━━━━━━━━━╮\n"
                "   ⚡  **P O N G**  ⚡\n"
                "╰━━━━━━━━━━━━━━━━━━━╯\n\n"
                f"◈ **Latency**  :  `{lat} ms`\n"
                f"◈ **Uptime**   :  `{h}h {m}m {s}s`\n"
                "◈ **Status**   :  `✅ Online`\n"
                "◈ **Engine**   :  `Healthy`\n\n"
                "_Apex Spam X • Always up_"
            )
            await msg.edit(text, parse_mode="md")
