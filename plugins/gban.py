import asyncio
from pyrogram import filters
from pyrogram.types import Message, InputMediaPhoto, InputMediaVideo
from pyrogram.errors import FloodWait
from GBan-head import app
from GBan-head.misc import SUDOERS
from GBan-head.utils import get_readable_time
from GBan-head.utils.database import (
    add_banned_user,
    remove_banned_user,
    is_banned_user,
    get_banned_users,
    get_banned_count,
    get_served_chats
)
from config import BANNED_USERS, GBAN_LOG_CHANNEL, GBAN_LOG_MEDIA

# ---------- Global Ban ----------
@app.on_message(filters.command(["gban", "globalban"]) & SUDOERS)
async def global_ban(client, message: Message):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text("Usage: /gban <user_id|@username> [reason]")

    # Extract user
    target = message.command[1] if len(message.command) > 1 else None
    reason = " ".join(message.command[2:]) if len(message.command) > 2 else "No reason"

    # Resolve username if needed
    if target.startswith("@"):
        try:
            user_obj = await client.get_users(target)
            target_id = user_obj.id
            target_mention = user_obj.mention
        except Exception:
            return await message.reply_text("❌ Cannot resolve username to user ID")
    else:
        try:
            target_id = int(target)
            user_obj = await client.get_users(target_id)
            target_mention = user_obj.mention
        except Exception:
            return await message.reply_text("❌ Invalid user ID")

    # Prevent banning self or other SUDOERS
    if target_id == message.from_user.id:
        return await message.reply_text("❌ You cannot GBAN yourself!")
    if target_id == app.id:
        return await message.reply_text("❌ You cannot GBAN the bot!")
    if target_id in SUDOERS:
        return await message.reply_text("❌ You cannot GBAN a SUDO user!")

    # Check if already GBANNED
    if await is_banned_user(target_id):
        return await message.reply_text(f"⚠️ {target_mention} is already GBANNED!")

    # Add to banned list
    if target_id not in BANNED_USERS:
        BANNED_USERS.add(target_id)

    # Ban in all served chats
    served_chats = [int(c["chat_id"]) for c in await get_served_chats()]
    time_expected = get_readable_time(len(served_chats))
    status_msg = await message.reply_text(f"⏳ Banning {target_mention} in {len(served_chats)} chats (~{time_expected})...")

    banned_count = 0
    for chat_id in served_chats:
        try:
            await app.ban_chat_member(chat_id, target_id)
            banned_count += 1
        except FloodWait as fw:
            await asyncio.sleep(int(fw.value))
        except:
            continue

    await add_banned_user(target_id)

    await status_msg.edit_text(f"✅ {target_mention} GBANNED in {banned_count} chats!\nReason: {reason}")

    # ---------- Log to GBAN channel ----------
    try:
        if GBAN_LOG_MEDIA:
            media = InputMediaPhoto(GBAN_LOG_MEDIA)  # Can be changed to InputMediaVideo if video
            await app.send_media_group(
                chat_id=GBAN_LOG_CHANNEL,
                media=[media]
            )
        await app.send_message(
            chat_id=GBAN_LOG_CHANNEL,
            text=f"🚫 **GBAN ALERT**\n\nUser: {target_mention} (`{target_id}`)\nBanned by: {message.from_user.mention}\nReason: {reason}\nTotal chats banned: {banned_count}"
        )
    except Exception as e:
        print(f"[WARN] Could not log GBAN to channel: {e}")


# ---------- Unban ----------
@app.on_message(filters.command(["ungban"]) & SUDOERS)
async def global_unban(client, message: Message):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text("Usage: /ungban <user_id|@username>")

    target = message.command[1]

    # Resolve username if needed
    if target.startswith("@"):
        try:
            user_obj = await client.get_users(target)
            target_id = user_obj.id
            target_mention = user_obj.mention
        except Exception:
            return await message.reply_text("❌ Cannot resolve username to user ID")
    else:
        try:
            target_id = int(target)
            user_obj = await client.get_users(target_id)
            target_mention = user_obj.mention
        except Exception:
            return await message.reply_text("❌ Invalid user ID")

    if not await is_banned_user(target_id):
        return await message.reply_text(f"⚠️ {target_mention} is not GBANNED!")

    # Remove from BANNED_USERS set
    if target_id in BANNED_USERS:
        BANNED_USERS.remove(target_id)

    served_chats = [int(c["chat_id"]) for c in await get_served_chats()]
    time_expected = get_readable_time(len(served_chats))
    status_msg = await message.reply_text(f"⏳ Unbanning {target_mention} in {len(served_chats)} chats (~{time_expected})...")

    unbanned_count = 0
    for chat_id in served_chats:
        try:
            await app.unban_chat_member(chat_id, target_id)
            unbanned_count += 1
        except FloodWait as fw:
            await asyncio.sleep(int(fw.value))
        except:
            continue

    await remove_banned_user(target_id)
    await status_msg.edit_text(f"✅ {target_mention} UNGBANNED in {unbanned_count} chats!")


# ---------- List GBAN Users ----------
@app.on_message(filters.command(["gbanlist", "gbannedusers"]) & SUDOERS)
async def gbanned_list(client, message: Message):
    count = await get_banned_count()
    if count == 0:
        return await message.reply_text("⚠️ No users are currently GBANNED.")

    users = await get_banned_users()
    text = "**🚫 GBANNED USERS**\n"
    for i, user_id in enumerate(users, start=1):
        try:
            user_obj = await app.get_users(user_id)
            mention = user_obj.mention or user_obj.first_name
        except Exception:
            mention = str(user_id)
        text += f"{i}. {mention}\n"

    await message.reply_text(text)
