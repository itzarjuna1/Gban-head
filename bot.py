import asyncio
import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import BadMsgNotification
from pyrogram import idle

import config
from database.mongo import db
from database.bots import register_bot, get_connected_bots
from database.sudo import add_sudo, remove_sudo, get_sudo_list
from database.gbans import add_gban, get_gban_list, watch_gbans  # include watch_gbans

# ---------- Create the bot client ----------
app = Client(
    "bot",
    api_id=int(config.API_ID),
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    workdir="./sessions"
)

# ---------- Helper Functions ----------
async def ensure_time_sync():
    now = int(time.time())
    print(f"[INFO] Current UNIX timestamp: {now}")
    await asyncio.sleep(1)

async def safe_start(app: Client):
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            await app.start()
            print("[INFO] Bot started successfully!")
            return True
        except BadMsgNotification:
            print(f"[WARN] BadMsgNotification [16] occurred, retrying... ({attempt}/{max_retries})")
            await ensure_time_sync()
    print("[ERROR] Could not start bot due to BadMsgNotification.")
    return False

def owner_only(user_id: int) -> bool:
    return user_id in config.SUDO_USERS

# ---------- Inline Keyboards ----------
def start_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️ Control Panel", callback_data="control_panel")],
        [InlineKeyboardButton("📢 Support", url=config.SUPPORT_CHAT)],
        [InlineKeyboardButton("🤖 Connected Bots", callback_data="connected_bots")]
    ])

# ---------- Command Handlers ----------
@app.on_message(filters.private & filters.command("start"))
async def start_handler(client: Client, message: Message):
    user_id = message.from_user.id
    if not owner_only(user_id):
        return await message.reply_text("❌ You are not allowed to use this bot.")

    await message.reply_text(
        "✅ Welcome! You are authorized.\nUse the buttons below or commands to manage GBAN.",
        reply_markup=start_buttons()
    )

@app.on_message(filters.private & filters.command("addsudo"))
async def addsudo_handler(client: Client, message: Message):
    user_id = message.from_user.id
    if not owner_only(user_id):
        return await message.reply_text("❌ You are not allowed to use this command.")

    if len(message.command) < 2:
        return await message.reply_text("Usage: /addsudo <user_id>")

    target_id = int(message.command[1])
    await add_sudo(target_id)
    await message.reply_text(f"✅ Added {target_id} as sudo.")

@app.on_message(filters.private & filters.command("delsudo"))
async def delsudo_handler(client: Client, message: Message):
    user_id = message.from_user.id
    if not owner_only(user_id):
        return await message.reply_text("❌ You are not allowed to use this command.")

    if len(message.command) < 2:
        return await message.reply_text("Usage: /delsudo <user_id>")

    target_id = int(message.command[1])
    await remove_sudo(target_id)
    await message.reply_text(f"✅ Removed {target_id} from sudo list.")

@app.on_message(filters.private & filters.command("sudolist"))
async def sudolist_handler(client: Client, message: Message):
    user_id = message.from_user.id
    if not owner_only(user_id):
        return await message.reply_text("❌ You are not allowed to use this command.")

    sudos = await get_sudo_list()
    if not sudos:
        return await message.reply_text("⚠️ No sudo users found.")

    text = "🛡️ Sudo Users:\n" + "\n".join(str(u) for u in sudos)
    await message.reply_text(text)

@app.on_message(filters.private & filters.command("gban"))
async def gban_handler(client: Client, message: Message):
    user_id = message.from_user.id
    if not owner_only(user_id):
        return await message.reply_text("❌ You are not allowed to use this command.")

    if len(message.command) < 2:
        return await message.reply_text("Usage: /gban <user_id> [reason]")

    # Handle username or user ID
    target = message.command[1]
    try:
        if target.startswith("@"):
            user_obj = await app.get_users(target)
            target_id = user_obj.id
        else:
            target_id = int(target)
    except Exception:
        return await message.reply_text("❌ Invalid user or ID.")

    reason = " ".join(message.command[2:]) or "No reason"
    await add_gban(target_id, reason, by=user_id)

    # Send log to GBAN_LOG_CHANNEL with optional media
    try:
        if config.GBAN_LOG_MEDIA:
            await app.send_photo(
                chat_id=config.GBAN_LOG_CHANNEL,
                photo=config.GBAN_LOG_MEDIA,
                caption=f"🚫 User `{target_id}` banned by {message.from_user.mention}\nReason: {reason}"
            )
        else:
            await app.send_message(
                chat_id=config.GBAN_LOG_CHANNEL,
                text=f"🚫 User `{target_id}` banned by {message.from_user.mention}\nReason: {reason}"
            )
    except Exception:
        pass

    await message.reply_text(f"✅ User `{target_id}` globally banned!\nReason: {reason}")

@app.on_message(filters.private & filters.command("gbanlist"))
async def gbanlist_handler(client: Client, message: Message):
    user_id = message.from_user.id
    if not owner_only(user_id):
        return await message.reply_text("❌ You are not allowed to use this command.")

    gbans = await get_gban_list()
    if not gbans:
        return await message.reply_text("⚠️ No users are globally banned.")

    text = "🚫 GBanned Users:\n" + "\n".join(f"{u['user_id']}: {u['reason']}" for u in gbans)
    await message.reply_text(text)

# ---------- Callback Query Handlers ----------
@app.on_callback_query()
async def button_handler(client, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id
    if not owner_only(user_id):
        return await callback_query.answer("❌ Not allowed", show_alert=True)

    if data == "control_panel":
        await callback_query.message.edit_text("⚙️ Control Panel")
    elif data == "connected_bots":
        bots = await get_connected_bots()
        if not bots:
            await callback_query.message.edit_text("⚠️ No bots connected.")
        else:
            text = "🤖 Connected Bots:\n" + "\n".join(f"@{b['bot_username']}" for b in bots)
            await callback_query.message.edit_text(text)

# ---------- Main Function ----------
async def main():
    os.makedirs("./sessions", exist_ok=True)

    started = await safe_start(app)
    if not started:
        return

    me = await app.get_me()
    await register_bot(me.id, me.username)
    print(f"[INFO] Bot connected as @{me.username} ({me.id})")
    print("[INFO] MongoDB database:", config.DB_NAME)
    print("[INFO] Bot is running...")

    # Start GBAN watcher so other bots sync
    asyncio.create_task(watch_gbans())

    await idle()
    await asyncio.Event().wait()

# ---------- Run ----------
if __name__ == "__main__":
    asyncio.run(main())
