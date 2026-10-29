# Apex Spam X — STRANGER-compatible re-exports
import config as _cfg
from config import (
    API_ID, API_HASH, OWNER_ID, CMD_HNDLR, HNDLR, START_TIME,
    HEROKU_APP_NAME, HEROKU_API_KEY, HEROKU_API,
    MONGO_DB_URI, SUDO_USERS, BOT_TOKENS, CLIENTS,
)

for _i in range(1, 11):
    _name = f"X{_i}"
    if hasattr(_cfg, _name):
        globals()[_name] = getattr(_cfg, _name)
