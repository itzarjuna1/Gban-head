import asyncio
import os
import time

from pyrogram import Client, filters, idle
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from pyrogram.errors import BadMsgNotification

import config
from database.bots import register_bot, get_connected_bots
from database.sudo import add_sudo, remove_sudo, get_sudo_list
from database.gbans import add_gban, get_gban_list

# ---------------- CLIENT ---------------- #

app = Client(
    name="gban_bot",
    api_id=int(config.API_ID),
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    workdir="sessions"
)

# ---------------- HELPERS ---------------- #

def is_authorized(user_id: int) -> bool:
    return user_id in config.SUDO_USERS


def start_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⚙ Control Panel", callback_data="panel")],
            [InlineKeyboardButton("🤖 Connected Bots", callback_data="bots")],
            [InlineKeyboardButton("📢 Support", url=config.SUPPORT_CHAT)],
        ]
    )


async def safe_start():
    for i in range(5):
        try:
            await app.start()
            print("[INFO] Bot started")
            return
        except BadMsgNotification:
            print(f"[WARN] BadMsgNotification [16], retry {i+1}/5")
            time.sleep(2)
    raise RuntimeError("Failed to start bot due to BadMsgNotification")

# ---------------- COMMANDS ---------------- #

@app.on_message(filters.private & filters.command("start"))
async def start_cmd(_, message: Message):
    if not is_authorized(message.from_user.id):
        return await message.reply_text("❌ You are not authorized to use this bot.")

    await message.reply_text(
        "✅ **GBAN Controller Online**\n\n"
        "Use commands or buttons below.",
        reply_markup=start_keyboard()
    )


@app.on_message(filters.private & filters.command("addsudo"))
async def addsudo_cmd(_, message: Message):
    if not is_authorized(message.from_user.id):
        return

    if len(message.command) < 2:
        return await message.reply_text("Usage: /addsudo <user_id>")

    uid = int(message.command[1])
    await add_sudo(uid)
    await message.reply_text(f"✅ Added `{uid}` as sudo.")


@app.on_message(filters.private & filters.command("delsudo"))
async def delsudo_cmd(_, message: Message):
    if not is_authorized(message.from_user.id):
        return

    if len(message.command) < 2:
        return await message.reply_text("Usage: /delsudo <user_id>")

    uid = int(message.command[1])
    await remove_sudo(uid)
    await message.reply_text(f"❌ Removed `{uid}` from sudo list.")


@app.on_message(filters.private & filters.command("sudolist"))
async def sudolist_cmd(_, message: Message):
    if not is_authorized(message.from_user.id):
        return

    sudos = await get_sudo_list()
    if not sudos:
        return await message.reply_text("No sudo users.")

    text = "**🛡 Sudo Users:**\n" + "\n".join(str(x) for x in sudos)
    await message.reply_text(text)


@app.on_message(filters.private & filters.command("gban"))
async def gban_cmd(_, message: Message):
    if not is_authorized(message.from_user.id):
        return

    if len(message.command) < 2:
        return await message.reply_text("Usage: /gban <user_id> [reason]")

    uid = int(message.command[1])
    reason = " ".join(message.command[2:]) or "No reason"

    await add_gban(uid, reason)
    await message.reply_text(f"🚫 **GBanned `{uid}`**\nReason: {reason}")


@app.on_message(filters.private & filters.command("gbanlist"))
async def gbanlist_cmd(_, message: Message):
    if not is_authorized(message.from_user.id):
        return

    gbans = await get_gban_list()
    if not gbans:
        return await message.reply_text("No GBanned users.")

    text = "**🚫 GBAN List:**\n"
    for u in gbans:
        text += f"- `{u['user_id']}` → {u['reason']}\n"

    await message.reply_text(text)

# ---------------- CALLBACKS ---------------- #

@app.on_callback_query()
async def callbacks(_, cb):
    if not is_authorized(cb.from_user.id):
        return await cb.answer("Not allowed", show_alert=True)

    if cb.data == "panel":
        await cb.message.edit_text("⚙ Control Panel\n\nUse commands.")

    elif cb.data == "bots":
        bots = await get_connected_bots()
        if not bots:
            await cb.message.edit_text("No connected bots.")
        else:
            text = "**🤖 Connected Bots:**\n"
            for b in bots:
                text += f"- @{b['bot_username']}\n"
            await cb.message.edit_text(text)

# ---------------- MAIN ---------------- #

async def main():
    os.makedirs("sessions", exist_ok=True)

    await safe_start()

    me = await app.get_me()
    await register_bot(me.id, me.username)

    print(f"[INFO] Logged in as @{me.username} ({me.id})")
    print("[INFO] Bot is RUNNING")

    await idle()

if __name__ == "__main__":
    asyncio.run(main())
