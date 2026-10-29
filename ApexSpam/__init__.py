import config as _cfg

# Re-export common names
from config import (
    API_ID, API_HASH, OWNER_ID, CMD_HNDLR, HNDLR, START_TIME,
    HEROKU_APP_NAME, HEROKU_API_KEY, HEROKU_API,
    MONGO_DB_URI, SUDO_USERS, CLIENTS, BOT_TOKEN,
)

# X1..X10 — all exist now in config
for _i in range(1, 11):
    globals()[f"X{_i}"] = getattr(_cfg, f"X{_i}")

# BOT_TOKEN2..BOT_TOKEN10
for _i in range(2, 11):
    globals()[f"BOT_TOKEN{_i}"] = getattr(_cfg, f"BOT_TOKEN{_i}", "")
