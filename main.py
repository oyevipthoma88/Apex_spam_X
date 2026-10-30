import asyncio
import importlib
import logging
from pathlib import Path

import config
from ApexSpam import fonts, buttons, state, logger as xlog

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
)
log = logging.getLogger("ApexSpam")


async def sync_loop():
    while True:
        try:
            from models.sudo import mongo_ids
            for uid in await mongo_ids():
                if uid not in config.SUDO_USERS:
                    config.SUDO_USERS.append(uid)
            await fonts.sync_from_db()
        except Exception as e:
            log.warning(f"sync_loop: {e}")
        await asyncio.sleep(30)


def load_modules():
    for path in sorted(Path("ApexSpam/modules").glob("*.py")):
        if path.name.startswith("__"):
            continue
        name = f"ApexSpam.modules.{path.stem}"
        try:
            mod = importlib.import_module(name)
            fn = getattr(mod, "register", None)
            if callable(fn):
                fn()
            state.LOADED[name] = "OK"
            log.info(f"✅ loaded: {name}")
        except Exception as e:
            state.LOADED[name] = f"{type(e).__name__}: {e}"
            log.exception(f"❌ failed: {name} -> {e}")


async def main():
    fonts.patch()
    await fonts.sync_from_db()
    log.info(f"active font: {fonts.ACTIVE_FONT}")

    try:
        config.create_clients()
        log.info(f"clients created: {len(config.CLIENTS)}")
    except Exception as e:
        log.exception(f"❌ client setup failed: {e}")
        return

    load_modules()

    started = 0
    for cli, tok in zip(config.CLIENTS, config.BOT_TOKENS):
        try:
            await cli.start(bot_token=tok)
            me = await cli.get_me()
            started += 1
            log.info(f"✅ logged in as @{me.username}")
        except Exception as e:
            log.exception(f"❌ login failed: {e}")

    if started == 0:
        log.error("❌ NO CLIENT STARTED")
        return

    if config.CLIENTS:
        xlog.set_client(config.CLIENTS[0])
        try:
            await xlog.log_bot("STARTUP", (await config.CLIENTS[0].get_me()).username or "bot",
                               f"clients={started}")
        except Exception as e:
            log.warning(f"startup log: {e}")

    asyncio.create_task(sync_loop())
    log.info(f"🚀 running with {started} client(s) | rich buttons: {buttons.HAS_STYLE}")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
