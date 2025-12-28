import asyncio
import os
import time
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import BadMsgNotification

import config
from database.mongo import db
from database.bots import register_bot, get_connected_bots
from database.sudo import add_sudo, remove_sudo, get_sudo_list
from database.gbans import add_gban, remove_gban, get_gban_list

# -------------------- Create bot client --------------------
app = Client(
    "gban_bot",
    api_id=int(config.API_ID),
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    workdir="./sessions"
)

# -------------------- Helper functions --------------------
async def safe_start(app: Client):
    """Start bot safely with retry for BadMsgNotification."""
    for attempt in range(5):
        try:
            await app.start()
            print("[✅] Bot started successfully!")
            return True
        except BadMsgNotification:
            print(f"[⚠️] BadMsgNotification occurred, retrying... ({attempt+1}/5)")
            await asyncio.sleep(1)
    print("[❌] Bot failed to start after retries.")
    return False

def owner_only(user_id: int) -> bool:
    return user_id in config.SUDO_USERS

def start_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️ Control Panel", callback_data="control_panel")],
        [InlineKeyboardButton("📢 Support", url=config.SUPPORT_CHAT)],
        [InlineKeyboardButton("🤖 Connected Bots", callback_data="connected_bots")]
    ])

# -------------------- Command Handlers --------------------
@app.on_message(filters.private & filters.command("start"))
async def start_handler(client: Client, message: Message):
    if not owner_only(message.from_user.id):
        return await message.reply_text("❌ You are not allowed to use this bot.")
    await message.reply_text(
        "✅ Welcome! You are authorized.\nUse buttons or commands to manage GBAN.",
        reply_markup=start_buttons()
    )

@app.on_message(filters.private & filters.command("addsudo"))
async def addsudo_handler(client: Client, message: Message):
    if not owner_only(message.from_user.id):
        return await message.reply_text("❌ Not allowed.")
    if len(message.command) < 2:
        return await message.reply_text("Usage: /addsudo <user_id>")
    target_id = int(message.command[1])
    await add_sudo(target_id)
    await message.reply_text(f"✅ Added {target_id} as sudo.")

@app.on_message(filters.private & filters.command("delsudo"))
async def delsudo_handler(client: Client, message: Message):
    if not owner_only(message.from_user.id):
        return await message.reply_text("❌ Not allowed.")
    if len(message.command) < 2:
        return await message.reply_text("Usage: /delsudo <user_id>")
    target_id = int(message.command[1])
    await remove_sudo(target_id)
    await message.reply_text(f"✅ Removed {target_id} from sudo list.")

@app.on_message(filters.private & filters.command("sudolist"))
async def sudolist_handler(client: Client, message: Message):
    if not owner_only(message.from_user.id):
        return await message.reply_text("❌ Not allowed.")
    sudos = await get_sudo_list()
    if not sudos:
        return await message.reply_text("⚠️ No sudo users found.")
    text = "🛡️ Sudo Users:\n" + "\n".join(str(u) for u in sudos)
    await message.reply_text(text)

@app.on_message(filters.private & filters.command("gban"))
async def gban_handler(client: Client, message: Message):
    if not owner_only(message.from_user.id):
        return await message.reply_text("❌ Not allowed.")
    if len(message.command) < 2:
        return await message.reply_text("Usage: /gban <user_id> [reason]")

    try:
        target_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ User ID must be an integer.")

    reason = " ".join(message.command[2:]) or "No reason"
    admin_id = message.from_user.id

    # Add to MongoDB GBAN
    await add_gban(target_id, reason, by=admin_id)

    # Notify GBAN log channel
    if config.GBAN_LOG_CHANNEL:
        if config.GBAN_LOG_MEDIA:
            await app.send_photo(
                chat_id=config.GBAN_LOG_CHANNEL,
                photo=config.GBAN_LOG_MEDIA,
                caption=f"🚫 User `{target_id}` GBANNED by `{admin_id}`\nReason: {reason}"
            )
        else:
            await app.send_message(
                chat_id=config.GBAN_LOG_CHANNEL,
                text=f"🚫 User `{target_id}` GBANNED by `{admin_id}`\nReason: {reason}"
            )

    # Notify connected bots
    bots = await get_connected_bots()
    for b in bots:
        # The other bots will pick this up via MongoDB change streams
        pass

    await message.reply_text(f"✅ User `{target_id}` globally banned!\nReason: {reason}")

@app.on_message(filters.private & filters.command("gbanlist"))
async def gbanlist_handler(client: Client, message: Message):
    if not owner_only(message.from_user.id):
        return await message.reply_text("❌ Not allowed.")
    gbans = await get_gban_list()
    if not gbans:
        return await message.reply_text("⚠️ No users are globally banned.")
    text = "🚫 GBanned Users:\n" + "\n".join(f"{u['user_id']}: {u['reason']}" for u in gbans)
    await message.reply_text(text)

# -------------------- Callback Query --------------------
@app.on_callback_query()
async def button_handler(client, callback_query):
    user_id = callback_query.from_user.id
    if not owner_only(user_id):
        return await callback_query.answer("❌ Not allowed", show_alert=True)

    data = callback_query.data
    if data == "control_panel":
        await callback_query.message.edit_text("⚙️ Control Panel")
    elif data == "connected_bots":
        bots = await get_connected_bots()
        if not bots:
            await callback_query.message.edit_text("⚠️ No bots connected.")
        else:
            text = "🤖 Connected Bots:\n" + "\n".join(f"@{b['bot_username']}" for b in bots)
            await callback_query.message.edit_text(text)

# -------------------- Main Function --------------------
async def main():
    os.makedirs("./sessions", exist_ok=True)

    if not await safe_start(app):
        return

    # Register main bot in MongoDB
    me = await app.get_me()
    await register_bot(me.id, me.username)

    print(f"[INFO] Bot connected as @{me.username} ({me.id})")
    print(f"[INFO] MongoDB database: {config.DB_NAME}")
    print("[INFO] Bot is running...")

    # Keep alive
    await idle()
    await asyncio.Event().wait()

# -------------------- Run --------------------
if __name__ == "__main__":
    asyncio.run(main())
