import asyncio
import importlib
import logging
from pathlib import Path

import config
from config import CLIENTS, BOT_TOKENS
from models.sudo import mongo_ids

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
)
log = logging.getLogger("ApexSpam")


async def sync_mongo_sudo():
    """Background task: merge Mongo sudo IDs into config.SUDO_USERS."""
    while True:
        try:
            ids = await mongo_ids()
            for uid in ids:
                if uid not in config.SUDO_USERS:
                    config.SUDO_USERS.append(uid)
        except Exception as e:
            log.warning(f"Mongo sync failed: {e}")
        await asyncio.sleep(60)


def load_modules():
    mod_dir = Path("ApexSpam/modules")
    for path in sorted(mod_dir.glob("*.py")):
        if path.name.startswith("__"):
            continue
        mod_name = f"ApexSpam.modules.{path.stem}"
        try:
            importlib.import_module(mod_name)
            log.info(f"✅ Loaded: {mod_name}")
        except Exception as e:
            log.exception(f"❌ Failed: {mod_name} → {e}")


async def main():
    if not CLIENTS:
        raise SystemExit("[!] No bot tokens")

    # IMPORTANT: modules load pehle (handlers register on unstarted clients),
    # phir clients start
    load_modules()

    for c, t in zip(CLIENTS, BOT_TOKENS):
        await c.start(bot_token=t)
        me = await c.get_me()
        log.info(f"✅ Logged in as @{me.username}")

    asyncio.create_task(sync_mongo_sudo())
    log.info(f"🚀 Running with {len(CLIENTS)} client(s)")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
