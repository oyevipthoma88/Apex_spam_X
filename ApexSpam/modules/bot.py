# © @ITSZApex
import sys
import heroku3

from config import X1, X2, X3, X4, X5, X6, X7, X8, X9, X10, OWNER_ID, SUDO_USERS, HEROKU_APP_NAME, HEROKU_API_KEY, CMD_HNDLR as hl

from os import execl, getenv
from telethon import events
from datetime import datetime


@X1.on(events.NewMessage(incoming=True, pattern=r"\%sping(?: |$)(.*)" % hl))
@X2.on(events.NewMessage(incoming=True, pattern=r"\%sping(?: |$)(.*)" % hl))
@X3.on(events.NewMessage(incoming=True, pattern=r"\%sping(?: |$)(.*)" % hl))
@X4.on(events.NewMessage(incoming=True, pattern=r"\%sping(?: |$)(.*)" % hl))
@X5.on(events.NewMessage(incoming=True, pattern=r"\%sping(?: |$)(.*)" % hl))
@X6.on(events.NewMessage(incoming=True, pattern=r"\%sping(?: |$)(.*)" % hl))
@X7.on(events.NewMessage(incoming=True, pattern=r"\%sping(?: |$)(.*)" % hl))
@X8.on(events.NewMessage(incoming=True, pattern=r"\%sping(?: |$)(.*)" % hl))
@X9.on(events.NewMessage(incoming=True, pattern=r"\%sping(?: |$)(.*)" % hl))
@X10.on(events.NewMessage(incoming=True, pattern=r"\%sping(?: |$)(.*)" % hl))
async def ping(e):
    if e.sender_id in SUDO_USERS:
        start = datetime.now()
        altron = await e.reply(f"» ™°‌𝗦 𝗧 𝗥 𝗔 𝗡 𝗚 𝗘 𝗥")
        end = datetime.now()
        mp = (end - start).microseconds / 1000
        await altron.edit(f"💫🥀 🫧 🇸𝗧 𝗥 𝗔 𝗡 𝗚 𝗘 𝗥\n» {mp} 𝙼𝚂")


@X1.on(events.NewMessage(incoming=True, pattern=r"\%sreboot(?: |$)(.*)" % hl))
@X2.on(events.NewMessage(incoming=True, pattern=r"\%sreboot(?: |$)(.*)" % hl))
@X3.on(events.NewMessage(incoming=True, pattern=r"\%sreboot(?: |$)(.*)" % hl))
@X4.on(events.NewMessage(incoming=True, pattern=r"\%sreboot(?: |$)(.*)" % hl))
@X5.on(events.NewMessage(incoming=True, pattern=r"\%sreboot(?: |$)(.*)" % hl))
@X6.on(events.NewMessage(incoming=True, pattern=r"\%sreboot(?: |$)(.*)" % hl))
@X7.on(events.NewMessage(incoming=True, pattern=r"\%sreboot(?: |$)(.*)" % hl))
@X8.on(events.NewMessage(incoming=True, pattern=r"\%sreboot(?: |$)(.*)" % hl))
@X9.on(events.NewMessage(incoming=True, pattern=r"\%sreboot(?: |$)(.*)" % hl))
@X10.on(events.NewMessage(incoming=True, pattern=r"\%sreboot(?: |$)(.*)" % hl))
async def restart(e):
    if e.sender_id in OWNER_ID:
        await e.reply(f"🥀ʀᴇsᴛᴀʀᴛɪɴɢ sᴛʀᴀɴɢᴇʀ ʙᴏᴛs🥀...")
        try:
            await X1.disconnect()
        except Exception:
            pass
        try:
            await X2.disconnect()
        except Exception:
            pass
        try:
            await X3.disconnect()
        except Exception:
            pass
        try:
            await X4.disconnect()
        except Exception:
            pass
        try:
            await X5.disconnect()
        except Exception:
            pass
        try:
            await X6.disconnect()
        except Exception:
            pass
        try:
            await X7.disconnect()
        except Exception:
            pass
        try:
            await X8.disconnect()
        except Exception:
            pass
        try:
            await X9.disconnect()
        except Exception:
            pass
        try:
            await X10.disconnect()
        except Exception:
            pass

        execl(sys.executable, sys.executable, *sys.argv)


@X1.on(events.NewMessage(incoming=True, pattern=r"\%ssudo(?: |$)(.*)" % hl))
@X2.on(events.NewMessage(incoming=True, pattern=r"\%ssudo(?: |$)(.*)" % hl))
@X3.on(events.NewMessage(incoming=True, pattern=r"\%ssudo(?: |$)(.*)" % hl))
@X4.on(events.NewMessage(incoming=True, pattern=r"\%ssudo(?: |$)(.*)" % hl))
@X5.on(events.NewMessage(incoming=True, pattern=r"\%ssudo(?: |$)(.*)" % hl))
@X6.on(events.NewMessage(incoming=True, pattern=r"\%ssudo(?: |$)(.*)" % hl))
@X7.on(events.NewMessage(incoming=True, pattern=r"\%ssudo(?: |$)(.*)" % hl))
@X8.on(events.NewMessage(incoming=True, pattern=r"\%ssudo(?: |$)(.*)" % hl))
@X9.on(events.NewMessage(incoming=True, pattern=r"\%ssudo(?: |$)(.*)" % hl))
@X10.on(events.NewMessage(incoming=True, pattern=r"\%ssudo(?: |$)(.*)" % hl))
async def addsudo(event):
    if event.sender_id == OWNER_ID:
        Heroku = heroku3.from_key(HEROKU_API_KEY)
        sudousers = getenv("SUDO_USERS", default=None)

        ok = await event.reply(f"» ᴀᴅᴅɪɴɢ ᴜsᴇʀ ᴀs sᴛʀᴀɴɢᴇʀ 💘sᴜᴅᴏ💘...🚀🚀")
        target = ""
        if HEROKU_APP_NAME is not None:
            app = Heroku.app(HEROKU_APP_NAME)
        else:
            await ok.edit("[HEROKU]:" "\nPlease Setup Your HEROKU_APP_NAME")
            return
        heroku_var = app.config()
        if event is None:
            return
        try:
            reply_msg = await event.get_reply_message()
            target = reply_msg.sender_id
        except:
            await ok.edit("» 🌺ʀᴇᴘʟʏ ᴛᴏ 𝙰 ᴜsᴇʀ🌺 !!")
            return

        if str(target) in sudousers:
            await ok.edit("» 🌸ᴛʜɪs ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ᴀ sᴜᴅᴏ ᴜsᴇʀ ᴏғ sᴛʀᴀɴɢᴇʀ ʙᴏᴛs🌸 !!")
        else:
            if len(sudousers) > 0:
                newsudo = f"{sudousers} {target}"
            else:
                newsudo = f"{target}"
            await ok.edit(f"» ɴᴇᴡ sᴜᴅᴏ ᴜsᴇʀ: {target}\n» 💖ʀᴇsᴛᴀʀᴛɪɴɢ sᴛʀᴀɴɢᴇʀ ʙᴏᴛs💖...`")
            heroku_var["SUDO_USERS"] = newsudo    

    elif event.sender_id in SUDO_USERS:
        await event.reply("» sᴏʀʀʏ, ᴏɴʟʏ ᴏᴡɴᴇʀ ᴄᴀɴ ᴀᴄᴇss ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")


@X1.on(events.NewMessage(incoming=True, pattern=r"\%srmsudo(?: |$)(.*)" % hl))
@X2.on(events.NewMessage(incoming=True, pattern=r"\%srmsudo(?: |$)(.*)" % hl))
@X3.on(events.NewMessage(incoming=True, pattern=r"\%srmsudo(?: |$)(.*)" % hl))
@X4.on(events.NewMessage(incoming=True, pattern=r"\%sremovesudo(?: |$)(.*)" % hl))
@X5.on(events.NewMessage(incoming=True, pattern=r"\%srmsudo(?: |$)(.*)" % hl))
@X6.on(events.NewMessage(incoming=True, pattern=r"\%srmsudo(?: |$)(.*)" % hl))
@X7.on(events.NewMessage(incoming=True, pattern=r"\%srmsudo(?: |$)(.*)" % hl))
@X8.on(events.NewMessage(incoming=True, pattern=r"\%srmsudo(?: |$)(.*)" % hl))
@X9.on(events.NewMessage(incoming=True, pattern=r"\%srmsudo(?: |$)(.*)" % hl))
@X10.on(events.NewMessage(incoming=True, pattern=r"\%srmsudo(?: |$)(.*)" % hl))
async def rmsudo(event):
    if event.sender_id == OWNER_ID:
        Heroku = heroku3.from_key(HEROKU_API_KEY)
        sudousers = getenv("SUDO_USERS", default=None)

        ok = await event.reply(f"» ʀᴇᴍᴏᴠɪɴɢ sᴜᴅᴏ ᴜsᴇʀ ɪɴ sᴛʀᴀɴɢᴇʀ 💘sᴜᴅᴏ ʟɪsᴛs💘...🚀🚀")
        target = ""
        if HEROKU_APP_NAME is not None:
            app = Heroku.app(HEROKU_APP_NAME)
        else:
            await ok.edit("[HEROKU]:" "\nPlease Setup Your HEROKU_APP_NAME")
            return
        heroku_var = app.config()
        if event is None:
            return
        try:
            reply_msg = await event.get_reply_message()
            target = reply_msg.sender_id
        except:
            await ok.edit("» 🌺ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ🌺 !!")
            return

        if str(target) in sudousers:
            newsudo = sudousers.replace(str(target), "").strip()
            await ok.edit(f"» sᴛʀᴀɴɢᴇʀ sᴜᴅᴏ ᴜsᴇʀ ʀᴇᴍᴏᴠᴇᴅ\n\n🛠️ sᴜᴅᴏ ᴜsᴇʀs: {newsudo} 🛠️")
            heroku_var["SUDO_USERS"] = newsudo
        else:
            await ok.edit("» 🌸ᴛʜɪs ᴜsᴇʀ ɪs ɴᴏᴛ ᴀ sᴜᴅᴏ ᴜsᴇʀ🌸 !!")

    elif event.sender_id in SUDO_USERS:
        await event.reply("» sᴏʀʀʏ, ᴏɴʟʏ ᴏᴡɴᴇʀ  ᴄᴀɴ ʀᴇᴍᴏᴠᴇ sᴜᴅᴏ.")


@X1.on(events.NewMessage(incoming=True, pattern=r"\%sudolist(?: |$)(.*)" % hl))
@X2.on(events.NewMessage(incoming=True, pattern=r"\%sudolist(?: |$)(.*)" % hl))
@X3.on(events.NewMessage(incoming=True, pattern=r"\%sudolist(?: |$)(.*)" % hl))
@X4.on(events.NewMessage(incoming=True, pattern=r"\%sudolist(?: |$)(.*)" % hl))
@X5.on(events.NewMessage(incoming=True, pattern=r"\%sudolist(?: |$)(.*)" % hl))
@X6.on(events.NewMessage(incoming=True, pattern=r"\%sudolist(?: |$)(.*)" % hl))
@X7.on(events.NewMessage(incoming=True, pattern=r"\%sudolist(?: |$)(.*)" % hl))
@X8.on(events.NewMessage(incoming=True, pattern=r"\%sudolist(?: |$)(.*)" % hl))
@X9.on(events.NewMessage(incoming=True, pattern=r"\%sudolist(?: |$)(.*)" % hl))
@X10.on(events.NewMessage(incoming=True, pattern=r"\%sudolist(?: |$)(.*)" % hl))
async def sudolist(event):
    if event.sender_id == OWNER_ID:
        Heroku = heroku3.from_key(HEROKU_API_KEY)
        sudousers = getenv("SUDO_USERS", default=None)

        if sudousers:
            await event.reply(f"» sᴜᴅᴏ ᴜsᴇʀs ʟɪsᴛ: {sudousers}")
        else:
            await event.reply("» ɴᴏ sᴜᴅᴏ ᴜsᴇʀs ᴀᴅᴅᴇᴅ.")

    elif event.sender_id in SUDO_USERS:
        await event.reply("» sᴏʀʀʏ, ᴏɴʟʏ 𝙾𝚆𝙽𝙴𝚁 ᴄᴀɴ ᴀᴄᴄᴇss ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")