from pyrogram.types import Message, CallbackQuery
from database.sudo import is_sudo


async def sudo_only_message(message: Message) -> bool:
    """
    Check sudo permission for messages
    """
    if not message.from_user:
        return False
    return await is_sudo(message.from_user.id)


async def sudo_only_callback(query: CallbackQuery) -> bool:
    """
    Check sudo permission for inline buttons
    """
    if not query.from_user:
        return False
    return await is_sudo(query.from_user.id)
