import time
import random

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from youtubesearchpython.__future__ import VideosSearch

import config
from config import BANNED_USERS
from strings import get_string

from Gban_head import app
from Gban_head.misc import _boot_
from Gban_head.plugins.sudo.sudoers import sudoers_list
from Gban_head.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from Gban_head.utils.decorators.language import LanguageStart
from Gban_head.utils.formatters import get_readable_time
from Gban_head.utils.inline import help_pannel, private_panel, start_panel

# --------------------------

NEXI_VID = [
    "https://telegra.ph/file/1a3c152717eb9d2e94dc2.mp4",
    "https://files.catbox.moe/ln00jb.mp4",
    "https://graph.org/file/83ebf52e8bbf138620de7.mp4",
    "https://files.catbox.moe/0fq20c.mp4",
    "https://graph.org/file/318eac81e3d4667edcb77.mp4",
    "https://graph.org/file/7c1aa59649fbf3ab422da.mp4",
    "https://files.catbox.moe/t0nepm.mp4",
]

# =========================
# PRIVATE /start
# =========================
@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)

    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        # HELP
        if name.startswith("help"):
            keyboard = help_pannel(_)
            return await message.reply_video(
                random.choice(NEXI_VID),
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
            )

        # SUDO LIST
        if name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=(
                        f"{message.from_user.mention} checked sudo list.\n\n"
                        f"ID: <code>{message.from_user.id}</code>\n"
                        f"Username: @{message.from_user.username}"
                    ),
                )
            return

        # TRACK INFO
        if name.startswith("inf"):
            m = await message.reply_text("🔎")
            query = name.replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"

            results = VideosSearch(query, limit=1)
            data = (await results.next())["result"][0]

            searched_text = _["start_6"].format(
                data["title"],
                data["duration"],
                data["viewCount"]["short"],
                data["publishedTime"],
                data["channel"]["link"],
                data["channel"]["name"],
                app.mention,
            )

            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=_["S_B_8"], url=data["link"]),
                        InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_CHAT),
                    ]
                ]
            )

            await m.delete()
            await app.send_photo(
                chat_id=message.chat.id,
                photo=data["thumbnails"][0]["url"].split("?")[0],
                caption=searched_text,
                reply_markup=key,
            )

            if await is_on_off(2):
                await app.send_message(
                    config.LOGGER_ID,
                    f"{message.from_user.mention} checked track info.",
                )

    # NORMAL START
    else:
        out = private_panel(_)
        await message.reply_video(
            random.choice(NEXI_VID),
            caption=_["start_2"].format(message.from_user.mention, app.mention),
            reply_markup=InlineKeyboardMarkup(out),
        )

        if await is_on_off(2):
            await app.send_message(
                config.LOGGER_ID,
                f"{message.from_user.mention} started the bot.",
            )

# =========================
# GROUP /start
# =========================
@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    uptime = int(time.time() - _boot_)
    out = start_panel(_)

    await message.reply_video(
        random.choice(NEXI_VID),
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
    )
    await add_served_chat(message.chat.id)

# =========================
# WELCOME HANDLER
# =========================
@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass

            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)

                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                await message.reply_video(
                    random.choice(NEXI_VID),
                    caption=_["start_3"].format(
                        message.from_user.mention,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()

        except Exception as e:
            print(e)
