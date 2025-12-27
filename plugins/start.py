from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
from utils.language import lang
from utils.permissions import sudo_only_message
from utils.panels import main_panel


@Client.on_message(filters.private & filters.command("start"))
async def start_private(app, message):
    # Check sudo / owner
    is_sudo = await sudo_only_message(message)

    if not is_sudo:
        # Normal user
        await message.reply_animation(
            animation=config.GBAN_LOG_MEDIA,
            caption=lang("start_normal")
        )
        return

    # Owner / Sudo panel
    await message.reply_animation(
        animation=config.GBAN_LOG_MEDIA,
        caption=lang("start_owner"),
        reply_markup=main_panel()
    )
