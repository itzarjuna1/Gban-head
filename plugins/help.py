from typing import Union

from pyrogram import filters, types, enums
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
    CallbackQuery,
)

from Gban_head import PARTH
from Gban_head.utils.inline import help_pannel
from Gban_head.utils.database import get_lang
from Gban_head.utils.decorators.language import LanguageStart, languageCB
from Gban_head.utils.inline.help import help_back_markup, private_help_panel
from Gban_head.utils.stuffs.buttons import BUTTONS
from Gban_head.utils.stuffs.helper import Helper

from config import BANNED_USERS, START_IMG_URL, SUPPORT_CHAT
from strings import get_string, helpers

# =========================
# PRIVATE /help
# =========================
@app.on_message(filters.command(["help"]) & filters.private & ~BANNED_USERS)
@app.on_callback_query(filters.regex("^settings_back_helper$") & ~BANNED_USERS)
async def helper_private(
    client,
    update: Union[Message, CallbackQuery],
):
    is_callback = isinstance(update, CallbackQuery)

    if is_callback:
        await update.answer()
        chat_id = update.message.chat.id
        language = await get_lang(chat_id)
        _ = get_string(language)

        keyboard = help_pannel(_, back=True)
        await update.edit_message_text(
            _["help_1"].format(SUPPORT_CHAT),
            reply_markup=keyboard,
        )

    else:
        try:
            await update.delete()
        except:
            pass

        language = await get_lang(update.chat.id)
        _ = get_string(language)

        keyboard = help_pannel(_)
        await update.reply_photo(
            photo=START_IMG_URL,
            caption=_["help_1"].format(SUPPORT_CHAT),
            reply_markup=keyboard,
        )

# =========================
# GROUP /help
# =========================
@app.on_message(filters.command(["help"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def help_com_group(client, message: Message, _):
    keyboard = private_help_panel(_)
    await message.reply_text(
        _["help_2"],
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# =========================
# HELP CALLBACK HANDLER
# =========================
@app.on_callback_query(filters.regex("^help_callback") & ~BANNED_USERS)
@languageCB
async def help_callback_handler(client, callback: CallbackQuery, _):
    cb = callback.data.split(None, 1)[1]
    keyboard = help_back_markup(_)

    help_map = {
        "hb1": helpers.HELP_1,
        "hb2": helpers.HELP_2,
        "hb3": helpers.HELP_3,
        "hb4": helpers.HELP_4,
        "hb5": helpers.HELP_5,
        "hb6": helpers.HELP_6,
        "hb7": helpers.HELP_7,
        "hb8": helpers.HELP_8,
        "hb9": helpers.HELP_9,
        "hb10": helpers.HELP_10,
        "hb11": helpers.HELP_11,
        "hb12": helpers.HELP_12,
        "hb13": helpers.HELP_13,
        "hb14": helpers.HELP_14,
        "hb15": helpers.HELP_15,
    }

    text = help_map.get(cb)
    if text:
        await callback.edit_message_text(text, reply_markup=keyboard)

# =========================
# MANAGE BOT CALLBACK
# =========================
@app.on_callback_query(filters.regex("^mbot_cb$") & ~BANNED_USERS)
async def manage_bot_cb(client, callback: CallbackQuery):
    await callback.edit_message_text(
        Helper.HELP_M,
        reply_markup=InlineKeyboardMarkup(BUTTONS.MBUTTON),
    )

# =========================
# MANAGE BOT PLUGIN
# =========================
@app.on_callback_query(filters.regex("^mplus") & ~BANNED_USERS)
async def manage_bot_plugin(client, callback: CallbackQuery):
    cb = callback.data.split(None, 1)[1]

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="mbot_cb")]]
    )

    if cb == "Okieeeeee":
        await callback.edit_message_text(
            "`something errors`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN,
        )
    else:
        text = getattr(Helper, cb, "`Unknown option`")
        await callback.edit_message_text(text, reply_markup=keyboard)
