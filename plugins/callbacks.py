from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.permissions import sudo_only_callback
from utils.language import lang
from utils.panels import main_panel
from database.bots import get_connected_bots


@Client.on_callback_query()
async def callbacks_handler(app, query):
    # Permission check
    if not await sudo_only_callback(query):
        return await query.answer(lang("access_denied"), show_alert=True)

    data = query.data

    # 🔄 Refresh Control Panel
    if data == "refresh":
        await query.message.edit_caption(
            caption=lang("start_owner"),
            reply_markup=main_panel()
        )

    # 🤖 Connected Bots
    elif data == "bots":
        bots = await get_connected_bots()

        if not bots:
            text = lang("bots_none")
        else:
            text = lang("bots_list_title") + "\n\n"
            for bot in bots:
                text += f"• @{bot.get('bot_username')} (`{bot['bot_id']}`)\n"

        await query.message.edit_caption(
            caption=text,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(lang("btn_back"), callback_data="refresh")]]
            )
        )

    else:
        await query.answer("⚠ Unknown action", show_alert=True)
