"""Run: heroku run python doctor.py -a <app>"""
import asyncio
import importlib
import os
import sys
import traceback


def env_check():
    print("── ENV ──")
    for k in ("API_ID", "API_HASH", "OWNER_ID", "MONGO_DB_URI", "BOT_TOKEN1"):
        v = os.getenv(k, "")
        print(f"{k}: {'SET' if v else 'MISSING'} ({len(v)} chars)")


def import_check():
    print("── IMPORT CORE ──")
    for name in ("config", "database", "ApexSpam", "ApexSpam.fonts",
                 "ApexSpam.ui", "ApexSpam.buttons", "ApexSpam.raid_engine"):
        try:
            importlib.import_module(name)
            print(f"✅ {name}")
        except Exception:
            print(f"❌ {name}")
            traceback.print_exc()


def module_check():
    print("── IMPORT MODULES ──")
    from pathlib import Path
    for p in sorted(Path("ApexSpam/modules").glob("*.py")):
        if p.name.startswith("__"):
            continue
        n = f"ApexSpam.modules.{p.stem}"
        try:
            importlib.import_module(n)
            print(f"✅ {n}")
        except Exception as e:
            print(f"❌ {n}: {e}")


async def mongo_check():
    print("── MONGO ──")
    try:
        from database import mongo_client
        if mongo_client is None:
            print("❌ mongo_client is None")
            return
        await mongo_client.admin.command("ping")
        print("✅ mongo ping ok")
    except Exception as e:
        print(f"❌ mongo: {e}")


async def client_check():
    print("── CLIENT ──")
    import config
    try:
        config.create_clients()
        c = config.CLIENTS[0]
        await c.connect()
        print("✅ telegram connect ok")
        try:
            await c.start(bot_token=config.BOT_TOKENS[0])
            me = await c.get_me()
            print(f"✅ login ok: @{me.username}")
        except Exception as e:
            print(f"❌ login: {e}")
        await c.disconnect()
    except Exception:
        traceback.print_exc()


if __name__ == "__main__":
    env_check()
    import_check()
    module_check()
    asyncio.run(mongo_check())
    asyncio.run(client_check())
    print("\n── DONE ──")
