import asyncio
import importlib
import logging
from pathlib import Path
from config import CLIENTS, BOT_TOKENS

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

async def start_client(client, token):
    await client.start(bot_token=token)
    me = await client.get_me()
    log.info(f"✅ Logged in as @{me.username}")
    return client

async def main():
    if not CLIENTS:
        raise SystemExit("[!] No bot tokens found (BOT_TOKEN1/2/3)")

    # Saare clients ko parallel mein start karein
    await asyncio.gather(*[start_client(c, t) for c, t in zip(CLIENTS, BOT_TOKENS)])

    # Modules load karein
    load_modules()

    log.info(f"🚀 Bot is now running with {len(CLIENTS)} client(s)...")
    
    # Event loop ko zinda rakhein (yeh run_until_disconnected se better hai)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
