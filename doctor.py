"""Heroku diagnostic: heroku run python doctor.py -a <app>"""
import asyncio
import importlib
import os
import traceback


def env_check():
    print("── ENV ──")
    for k in ("API_ID", "API_HASH", "OWNER_ID", "MONGO_DB_URI", "BOT_TOKEN1"):
        v = os.getenv(k, "") or ""
        print(f"{k}: {'SET ('+str(len(v))+' chars)' if v else 'MISSING'}")


def import_check():
    print("\n── CORE IMPORTS ──")
    for name in ("config", "database", "ApexSpam", "ApexSpam.fonts",
                 "ApexSpam.ui", "ApexSpam.buttons", "ApexSpam.raid_engine"):
        try:
            importlib.import_module(name)
            print(f"OK  {name}")
        except Exception as e:
            print(f"ERR {name}: {e}")
            traceback.print_exc()


def module_check():
    print("\n── MODULES ──")
    from pathlib import Path
    for p in sorted(Path("ApexSpam/modules").glob("*.py")):
        if p.name.startswith("__"):
            continue
        n = f"ApexSpam.modules.{p.stem}"
        try:
            importlib.import_module(n)
            print(f"OK  {n}")
        except Exception as e:
            print(f"ERR {n}: {e}")


async def mongo_check():
    print("\n── MONGO ──")
    try:
        from database import mongo_client
        if mongo_client is None:
            print("ERR mongo_client None (MONGO_DB_URI missing?)")
            return
        await mongo_client.admin.command("ping")
        print("OK  mongo ping")
    except Exception as e:
        print(f"ERR mongo: {e}")


async def client_check():
    print("\n── TELEGRAM ──")
    import config
    try:
        config.create_clients()
    except Exception as e:
        print(f"ERR create_clients: {e}")
        traceback.print_exc()
        return
    if not config.CLIENTS:
        print("ERR no clients built")
        return
    c = config.CLIENTS[0]
    try:
        await c.connect()
        print("OK  telegram connect")
    except Exception as e:
        print(f"ERR connect: {e}")
        return
    try:
        await c.start(bot_token=config.BOT_TOKENS[0])
        me = await c.get_me()
        print(f"OK  login @{me.username}")
    except Exception as e:
        print(f"ERR login: {e}")
    try:
        await c.disconnect()
    except Exception:
        pass


if __name__ == "__main__":
    env_check()
    import_check()
    module_check()
    asyncio.run(mongo_check())
    asyncio.run(client_check())
    print("\n── DONE ──")
