"""Apex Spam X — callback ack + media-safe edit."""
import logging

log = logging.getLogger("ApexSpam.respond")


async def ack(event, text=None, alert=False):
    try:
        await event.answer(text or "", alert=alert)
    except Exception as e:
        log.debug(f"ack failed: {e}")


def _has_media(msg):
    if not msg:
        return False
    try:
        return bool(msg.photo or msg.document or msg.video or msg.audio or msg.gif)
    except Exception:
        return False


async def edit(event, text, buttons=None):
    """Edit safely — handles photo, caption, not-modified, fallback to new."""
    try:
        if _has_media(getattr(event, "message", None)):
            # Photo message — try caption edit first
            try:
                await event.edit(caption=text, buttons=buttons, parse_mode="html")
                return True
            except Exception as e:
                # Caption edit failed → send fresh text message
                log.info(f"caption edit failed, sending new: {e}")
                await event.respond(text, buttons=buttons, parse_mode="html")
                return True
        # Text message — normal edit
        try:
            await event.edit(text, buttons=buttons, parse_mode="html")
            return True
        except Exception as e:
            if "not modified" in str(e).lower():
                return True
            log.info(f"text edit failed, sending new: {e}")
            await event.respond(text, buttons=buttons, parse_mode="html")
            return True
    except Exception as e:
        log.warning(f"edit failed completely: {e}")
        return False
