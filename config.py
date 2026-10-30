"""Apex Spam X — env + lazy client factory (no import-time side effects)."""
import os
import sys
import time

API_ID = int(os.getenv("API_ID", "0") or 0)
API_HASH = (os.getenv("API_HASH") or "").strip()
OWNER_ID = int(os.getenv("OWNER_ID", "0") or 0)

CMD_HNDLR = os.getenv("CMD_HNDLR", ".") or "."
HNDLR = CMD_HNDLR
hl = CMD_HNDLR

START_TIME = time.time()

HEROKU_APP_NAME = (os.getenv("HEROKU_APP_NAME") or "").strip()
HEROKU_API_KEY = (os.getenv("HEROKU_API_KEY") or "").strip()
HEROKU_API = HEROKU_API_KEY
MONGO_DB_URI = (os.getenv("MONGO_DB_URI") or "").strip()

SUDO_USERS = [
    int(x) for x in os.getenv("SUDO_USERS", "").replace(",", " ").split()
    if x.strip().lstrip("-").isdigit()
]
if OWNER_ID and OWNER_ID not in SUDO_USERS:
    SUDO_USERS.append(OWNER_ID)

# placeholders so `from ApexSpam import X1` never explodes at import time
CLIENTS = []
BOT_TOKENS = []
BOT_TOKEN = ""
for _i in range(1, 11):
    globals()[f"X{_i}"] = None
for _i in range(2, 11):
    globals()[f"BOT_TOKEN{_i}"] = ""

APEX_OWNER = []


def _collect_tokens():
    out = []
    for i in range(1, 11):
        t = (os.getenv(f"BOT_TOKEN{i}") or "").strip()
        if i == 1 and not t:
            t = (os.getenv("BOT_TOKEN") or "").strip()
        if t:
            out.append(t)
    return out


def create_clients():
    """Create Telegram clients INSIDE a running loop. Returns list of clients."""
    from telethon import TelegramClient
    from telethon.sessions import MemorySession

    if not API_ID or not API_HASH:
        raise RuntimeError("API_ID / API_HASH missing in env")

    tokens = _collect_tokens()
    if not tokens:
        raise RuntimeError("No BOT_TOKEN1..10 set")

    clients = []
    for idx, tok in enumerate(tokens, start=1):
        cli = TelegramClient(
            MemorySession(),
            API_ID,
            API_HASH,
            connection_retries=5,
            retry_delay=2,
        )
        clients.append(cli)
        setattr(sys.modules[__name__], f"X{idx}", cli)

    global BOT_TOKEN
    BOT_TOKEN = tokens[0]

    CLIENTS.clear()
    CLIENTS.extend(clients)
    BOT_TOKENS.clear()
    BOT_TOKENS.extend(tokens)
    return clients
