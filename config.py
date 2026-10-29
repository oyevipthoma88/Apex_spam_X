import os
import time
from telethon import TelegramClient

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
CMD_HNDLR = os.getenv("CMD_HNDLR", ".")
START_TIME = time.time()

BOT_TOKENS = [
    t.strip()
    for t in (
        os.getenv("BOT_TOKEN1", ""),
        os.getenv("BOT_TOKEN2", ""),
        os.getenv("BOT_TOKEN3", ""),
    )
    if t.strip()
]

CLIENTS = [TelegramClient(f"X{i+1}", API_ID, API_HASH) for i in range(len(BOT_TOKENS))]
