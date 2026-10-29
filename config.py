import os
import time
from telethon import TelegramClient

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
CMD_HNDLR = os.getenv("CMD_HNDLR", ".")
START_TIME = time.time()

def _mk(name: str, token_env: str):
    token = os.getenv(token_env, "").strip()
    if not token:
        return None
    return TelegramClient(name, API_ID, API_HASH).start(bot_token=token)

X1 = _mk("X1", "BOT_TOKEN1")
X2 = _mk("X2", "BOT_TOKEN2")
X3 = _mk("X3", "BOT_TOKEN3")

CLIENTS = [c for c in (X1, X2, X3) if c is not None]
