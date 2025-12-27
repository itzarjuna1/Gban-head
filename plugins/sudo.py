from pyrogram import Client, filters
from pyrogram.types import Message

import config
from utils.permissions import sudo_only_message
from utils.language import lang
from database.sudo import add_sudo, del_sudo, get_sudo_list


def is_owner(user_id: int) -> bool:
    return user_id == config.OWNER_ID


@Client.on_message(filters.private & filters.command("addsudo"))
async def addsudo_handler(app, message: Message):
    if not is_owner(message.from_user.id):
        return await message.reply_text(lang("access_denied"))

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) >= 2:
        user_id = int(message.command[1])
    else:
        return await message.reply_text("Usage: /addsudo <user_id> or reply")

    await add_sudo(user_id)
    await message.reply_text(lang("sudo_added"))


@Client.on_message(filters.private & filters.command("delsudo"))
async def delsudo_handler(app, message: Message):
    if not is_owner(message.from_user.id):
        return await message.reply_text(lang("access_denied"))

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) >= 2:
        user_id = int(message.command[1])
    else:
        return await message.reply_text("Usage: /delsudo <user_id> or reply")

    success = await del_sudo(user_id)
    if not success:
        return await message.reply_text("❌ Owner cannot be removed.")

    await message.reply_text(lang("sudo_removed"))


@Client.on_message(filters.private & filters.command("sudolist"))
async def sudolist_handler(app, message: Message):
    if not await sudo_only_message(message):
        return await message.reply_text(lang("access_denied"))

    sudos = await get_sudo_list()
    text = lang("sudo_list_title") + "\n\n"

    for u in sudos:
        tag = "👑 OWNER" if u.get("is_owner") else "🔹 SUDO"
        text += f"{tag} `{u['user_id']}`\n"

    await message.reply_text(text)
