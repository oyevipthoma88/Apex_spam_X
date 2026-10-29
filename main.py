import asyncio
import importlib
import logging
from pathlib import Path

import config
from config import BOT_TOKENS
from models.sudo import mongo_ids
from ApexSpam import fonts, buttons

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
)
log = logging.getLogger("ApexSpam")


async def sync_loop():
    while True:
        try:
            for uid in await mongo_ids():
                if uid not in config.SUDO_USERS:
                    config.SUDO_USERS.append(uid)
            await fonts.sync_from_db()
        except Exception as e:
            log.warning(f"sync_loop: {e}")
        await asyncio.sleep(20)


def load_modules():
    mod_dir = Path("ApexSpam/modules")
    for path in sorted(mod_dir.glob("*.py")):
        if path.name.startswith("__"):
            continue
        mod_name = f"ApexSpam.modules.{path.stem}"
        try:
            mod = importlib.import_module(mod_name)
            if hasattr(mod, "register") and callable(mod.register):
                mod.register()
                log.info(f"✅ Loaded+registered: {mod_name}")
            else:
                log.info(f"✅ Loaded: {mod_name}")
        except Exception as e:
            log.exception(f"❌ Failed: {mod_name} → {e}")


async def main():
    fonts.patch()
    await fonts.sync_from_db()
    log.info(f"🎨 Active font: {fonts.ACTIVE_FONT}")
    load_modules()
    for client, token in BOT_TOKENS:
        try:
            await client.start(bot_token=token)
            me = await client.get_me()
            log.info(f"✅ Logged in as @{me.username}")
        except Exception as e:
            log.exception(f"❌ Login failed: {e}")
    asyncio.create_task(sync_loop())
    log.info(f"🚀 Running with {len(BOT_TOKENS)} client(s) | colored buttons: {buttons.HAS_STYLE}")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
