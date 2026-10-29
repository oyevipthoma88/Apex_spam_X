"""Shared premium UI helpers for Apex Spam X."""

DIV_TOP = "╭━━━━━━━━━━━━━━━━━━━━╮"
DIV_BOT = "╰━━━━━━━━━━━━━━━━━━━━╯"


def header(title: str, emoji: str = "⚡") -> str:
    spaced = " ".join(title.upper())
    return f"{DIV_TOP}\n   {emoji}  **{spaced}**  {emoji}\n{DIV_BOT}"


def section(name: str) -> str:
    return f"╭─〔 **{name}** 〕─╮"


def kv(key: str, value) -> str:
    return f"◈ **{key}**  :  `{value}`"


def note(text: str) -> str:
    return f"_{text}_"
