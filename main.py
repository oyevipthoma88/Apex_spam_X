import asyncio
import importlib
import logging
from pathlib import Path
from telethon import TelegramClient
from telethon.sessions import MemorySession

import config
from config import API_ID, API_HASH, BOT_TOKENS

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
)
log = logging.getLogger("ApexSpam")


def load_modules():
    mod_dir = Path("ApexSpam/modules")
    for path in sorted(mod_dir.glob("*.py")):
        if path.name.startswith("__"):
            continue
        mod_name = f"ApexSpam.modules.{path.stem}"
        try:
            mod = importlib.import_module(mod_name)
            if hasattr(mod, "register"):
                mod.register()
                log.info(f"✅ Loaded: {mod_name}")
            else:
                log.warning(f"⚠️ {mod_name} has no register()")
        except Exception as e:
            log.exception(f"❌ Failed: {mod_name} → {e}")


async def start_one(idx: int, token: str):
    loop = asyncio.get_running_loop()
    client = TelegramClient(
        f"X{idx+1}",
        API_ID,
        API_HASH,
        loop=loop,                 # <-- SAME loop, fixes dispatch
        session=MemorySession(),   # <-- no SQLite file on Heroku
    )
    await client.start(bot_token=token)
    me = await client.get_me()
    log.info(f"✅ Logged in as @{me.username}")
    config.CLIENTS.append(client)
    return client


async def main():
    for i, token in enumerate(BOT_TOKENS):
        await start_one(i, token)

    # Modules load ONLY after clients exist and loop is running
    load_modules()

    log.info(f"🚀 Bot is now running with {len(config.CLIENTS)} client(s)...")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
