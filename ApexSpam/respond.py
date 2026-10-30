"""Apex Spam X — callback ack + safe edit with error logging."""
import logging

log = logging.getLogger("ApexSpam.respond")


async def ack(event, text=None, alert=False):
    try:
        await event.answer(text or "", alert=alert)
    except Exception as e:
        log.debug(f"ack failed: {e}")


async def edit(event, text, buttons=None):
    try:
        await event.edit(text, buttons=buttons, parse_mode="html")
        return True
    except Exception as e:
        msg = str(e).lower()
        if "not modified" in msg:
            return True
        log.warning(f"edit failed: {e}")
        return False
