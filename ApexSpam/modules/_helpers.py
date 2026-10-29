from config import OWNER_ID
from models.sudo import is_sudo


def register():
    pass


async def has_perm(event) -> bool:
    if event.sender_id == OWNER_ID:
        return True
    return await is_sudo(event.sender_id)


async def resolve_user(event, arg: str):
    if arg and arg.isdigit():
        return int(arg)
    if event.reply_to_msg_id:
        r = await event.get_reply_message()
        return r.sender_id
    if arg:
        try:
            ent = await event.client.get_entity(arg)
            return ent.id
        except Exception:
            return None
    return None
