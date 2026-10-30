"""Apex Spam X — callback ack + media-safe edit (text, not caption)."""
import logging

log = logging.getLogger("ApexSpam.respond")


async def ack(event, text=None, alert=False):
    try:
        await event.answer(text or "", alert=alert)
    except Exception as e:
        log.debug(f"ack failed: {e}")


async def edit(event, text, buttons=None):
    """Edit safely — Telethon auto-detects media; pass `text` only."""
    try:
        # Telethon `edit` handles caption automatically when message has media.
        try:
            await event.edit(text, buttons=buttons, parse_mode="html")
            return True
        except Exception as e:
            msg = str(e).lower()
            if "not modified" in msg:
                return True
            log.info(f"edit failed, sending new: {e}")
            try:
                await event.respond(text, buttons=buttons, parse_mode="html")
                return True
            except Exception as ex2:
                log.warning(f"respond fallback failed: {ex2}")
                return False
    except Exception as e:
        log.warning(f"edit outer failed: {e}")
        return False
