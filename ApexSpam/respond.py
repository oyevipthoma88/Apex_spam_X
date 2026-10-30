"""Apex Spam X — callback ack + safe edit (no flood, no MessageNotModified)."""


async def ack(event, text=None, alert=False):
    try:
        await event.answer(text or "", alert=alert)
    except Exception:
        pass


async def edit(event, text, buttons=None):
    try:
        await event.edit(text, buttons=buttons, parse_mode="html")
        return True
    except Exception as e:
        if "not modified" in str(e).lower():
            return True
        return False
