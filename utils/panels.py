from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.language import lang
import config


def main_panel():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(lang("btn_gban"), callback_data="gban"),
                InlineKeyboardButton(lang("btn_ungban"), callback_data="ungban")
            ],
            [
                InlineKeyboardButton(lang("btn_gban_list"), callback_data="gban_list"),
                InlineKeyboardButton(lang("btn_sudo_list"), callback_data="sudo_list")
            ],
            [
                InlineKeyboardButton(lang("btn_connected_bots"), callback_data="bots")
            ],
            [
                InlineKeyboardButton(lang("btn_control_panel"), callback_data="refresh"),
                InlineKeyboardButton(lang("btn_support"), url=config.SUPPORT_CHAT)
            ]
        ]
    )
