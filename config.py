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

# Env fallback sudo IDs + owner
SUDO_USERS = [
    int(x) for x in os.getenv("SUDO_USERS", "").replace(",", " ").split()
    if x.strip().isdigit()
]
if OWNER_ID and OWNER_ID not in SUDO_USERS:
    SUDO_USERS.append(OWNER_ID)

# Export BOT_TOKEN (singular) + BOT_TOKEN2..10 for Apex Spam X module compat
BOT_TOKEN = os.getenv("BOT_TOKEN1", "").strip() or os.getenv("BOT_TOKEN", "").strip()
for _i in range(2, 11):
    globals()[f"BOT_TOKEN{_i}"] = os.getenv(f"BOT_TOKEN{_i}", "").strip()

# ALWAYS create X1..X10 (modules import all 10 unconditionally)
CLIENTS = []
BOT_TOKENS = []  # (client, token) pairs — only for non-empty tokens
for i in range(1, 11):
    token = os.getenv(f"BOT_TOKEN{i}", "").strip()
    c = TelegramClient(f"X{i}", API_ID, API_HASH)
    globals()[f"X{i}"] = c
    CLIENTS.append(c)
    if token:
        BOT_TOKENS.append((c, token))

if not BOT_TOKENS:
    raise SystemExit("[!] No BOT_TOKEN1..10 set")
APEX_OWNER = []
