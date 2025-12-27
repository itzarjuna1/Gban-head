from pyrogram import Client, filters
from pyrogram.types import Message

from utils.permissions import sudo_only_message
from utils.language import lang
from database.gbans import add_gban
from utils.gban_logger import send_gban_log


@Client.on_message(filters.command("gban") & filters.private)
async def gban_handler(app, message: Message):
    # Permission check
    if not await sudo_only_message(message):
        return await message.reply_text(lang("access_denied"))

    # Target detection
    if message.reply_to_message:
        target = message.reply_to_message.from_user
        if not target:
            return
        user_id = target.id
        reason = " ".join(message.command[1:]) or "No reason provided"

    elif len(message.command) >= 2:
        try:
            user_id = int(message.command[1])
        except ValueError:
            return await message.reply_text("Invalid user ID.")
        reason = " ".join(message.command[2:]) or "No reason provided"

    else:
        return await message.reply_text("Usage: /gban <user_id> or reply to a user")

    # Write to MongoDB (THIS triggers all bots)
    await add_gban(
        user_id=user_id,
        reason=reason,
        by=message.from_user.id
    )

    # Confirmation to command issuer
    await message.reply_text(lang("gban_done"))

    # Optional: log origin action
    await send_gban_log(
        app=app,
        user_id=user_id,
        reason=reason,
        origin="Owner/Sudo Command",
        affected_chats=0,
        is_unban=False
    )
