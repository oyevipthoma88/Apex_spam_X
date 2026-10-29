import os
import time
from telethon import TelegramClient  # noqa

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
CMD_HNDLR = os.getenv("CMD_HNDLR", ".")
HEROKU_APP_NAME = os.getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = os.getenv("HEROKU_API_KEY")
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

if not API_ID or not API_HASH:
    raise SystemExit("[!] API_ID / API_HASH missing")
if not OWNER_ID:
    raise SystemExit("[!] OWNER_ID missing")
if not BOT_TOKENS:
    raise SystemExit("[!] BOT_TOKEN1/2/3 missing")

# IMPORTANT: Populated inside main.py AFTER loop is running
CLIENTS = []
