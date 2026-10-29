import asyncio
import importlib
import logging
from pathlib import Path
from config import CLIENTS

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

async def main():
    if not CLIENTS:
        raise SystemExit("[!] No bot tokens found (BOT_TOKEN1/2/3)")
    load_modules()
    log.info(f"🚀 Starting {len(CLIENTS)} client(s)...")
    await asyncio.gather(*[c.run_until_disconnected() for c in CLIENTS])

if __name__ == "__main__":
    asyncio.run(main())
