import re
from config import CMD_HNDLR


def cmd(name: str) -> str:
    return rf"{re.escape(CMD_HNDLR)}{name}(?: |$)"
