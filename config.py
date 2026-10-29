import os
import time
from telethon import TelegramClient

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
CMD_HNDLR = os.getenv("CMD_HNDLR", ".")
HNDLR = CMD_HNDLR
START_TIME = time.time()

HEROKU_APP_NAME = os.getenv("HEROKU_APP_NAME", "").strip()
HEROKU_API_KEY = os.getenv("HEROKU_API_KEY", "").strip()
HEROKU_API = HEROKU_API_KEY

MONGO_DB_URI = os.getenv("MONGO_DB_URI", "").strip()

# MUTABLE list — modules isse import karte hain, same object shared
SUDO_USERS = [
    int(x) for x in os.getenv("SUDO_USERS", "").replace(",", " ").split()
    if x.strip().isdigit()
]

BOT_TOKENS = []
for i in range(1, 11):
    t = os.getenv(f"BOT_TOKEN{i}", "").strip()
    if t:
        BOT_TOKENS.append(t)

# Clients — .start() sirf main.py me hoga (loop mismatch avoid)
CLIENTS = []
for i, _ in enumerate(BOT_TOKENS):
    c = TelegramClient(f"X{i+1}", API_ID, API_HASH)
    CLIENTS.append(c)
    globals()[f"X{i+1}"] = c
