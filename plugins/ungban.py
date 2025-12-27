from pyrogram import Client, filters
from pyrogram.types import Message

from utils.permissions import sudo_only_message
from utils.language import lang
from database.gbans import remove_gban
from utils.gban_logger import send_gban_log


@Client.on_message(filters.private & filters.command("ungban"))
async def ungban_handler(app, message: Message):
    if not await sudo_only_message(message):
        return await message.reply_text(lang("access_denied"))

    if message.reply_to_message:
        target = message.reply_to_message.from_user
        if not target:
            return
        user_id = target.id
        reason = "Ungban requested"
    elif len(message.command) >= 2:
        try:
            user_id = int(message.command[1])
        except ValueError:
            return await message.reply_text("Invalid user ID.")
        reason = "Ungban requested"
    else:
        return await message.reply_text("Usage: /ungban <user_id> or reply")

    await remove_gban(user_id)

    await message.reply_text(lang("ungban_done"))

    # Log unban
    await send_gban_log(
        app=app,
        user_id=user_id,
        reason=reason,
        origin="Owner/Sudo Command",
        affected_chats=0,
        is_unban=True
    )
