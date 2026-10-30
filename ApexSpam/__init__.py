"""Apex Spam X — lazy re-exports from config (PEP 562)."""
import config as _cfg

_EAGER = (
    "API_ID", "API_HASH", "OWNER_ID", "CMD_HNDLR", "HNDLR", "hl",
    "START_TIME", "HEROKU_APP_NAME", "HEROKU_API_KEY", "HEROKU_API",
    "MONGO_DB_URI", "SUDO_USERS", "CLIENTS", "BOT_TOKENS",
    "BOT_TOKEN", "APEX_OWNER", "USER_SESSION", "LOG_CHANNEL_ID",
)
for _n in _EAGER:
    globals()[_n] = getattr(_cfg, _n, None)


def __getattr__(name):
    # X1..X10, BOT_TOKEN2..10 etc. resolved lazily from config
    try:
        return getattr(_cfg, name)
    except AttributeError:
        raise AttributeError(f"module 'ApexSpam' has no attribute {name!r}")
