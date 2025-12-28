import asyncio
from pyrogram import Client, filters, idle, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
import config

from database.mongo import db
from database.bots import register_bot, get_connected_bots
from database.sudo import add_sudo, remove_sudo, get_sudo_list
from database.gbans import add_gban, get_gban_list

import logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class GBANBot(Client):
    def __init__(self):
        LOGGER.info("Starting GBAN Bot...")
        super().__init__(
            "GBANBot",
            api_id=int(config.API_ID),
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            workers=1,
        )
        self.username = None

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.id = me.id
        self.username = me.username
        LOGGER.info(f"GBAN Bot Started as @{self.username} ({self.id})")

        # Register bot in MongoDB
        await register_bot(self.id, self.username)

    async def stop(self):
        await super().stop()


# ---------- Helper ----------
def owner_only(user_id: int):
    return user_id in config.SUDO_USERS


# ---------- Inline Keyboards ----------
def start_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️ Control Panel", callback_data="control_panel")],
        [InlineKeyboardButton("📢 Support", url=config.SUPPORT_CHAT)],
        [InlineKeyboardButton("🤖 Connected Bots", callback_data="connected_bots")]
    ])


# ---------- Command Handlers ----------
def register_handlers(bot: GBANBot):
    @bot.on_message(filters.private & filters.command("start"))
    async def start_handler(_, message):
        if not owner_only(message.from_user.id):
            return await message.reply_text("❌ You are not allowed to use this bot.")
        await message.reply_text(
            "✅ Welcome! You are authorized.\nUse buttons or commands to manage GBAN.",
            reply_markup=start_buttons()
        )

    @bot.on_message(filters.private & filters.command("addsudo"))
    async def addsudo_handler(_, message):
        if not owner_only(message.from_user.id):
            return await message.reply_text("❌ Not allowed.")
        if len(message.command) < 2:
            return await message.reply_text("Usage: /addsudo <user_id>")
        target_id = int(message.command[1])
        await add_sudo(target_id)
        await message.reply_text(f"✅ Added {target_id} as sudo.")

    @bot.on_message(filters.private & filters.command("delsudo"))
    async def delsudo_handler(_, message):
        if not owner_only(message.from_user.id):
            return await message.reply_text("❌ Not allowed.")
        if len(message.command) < 2:
            return await message.reply_text("Usage: /delsudo <user_id>")
        target_id = int(message.command[1])
        await remove_sudo(target_id)
        await message.reply_text(f"✅ Removed {target_id} from sudo list.")

    @bot.on_message(filters.private & filters.command("sudolist"))
    async def sudolist_handler(_, message):
        if not owner_only(message.from_user.id):
            return await message.reply_text("❌ Not allowed.")
        sudos = await get_sudo_list()
        text = "🛡️ Sudo Users:\n" + "\n".join(str(u) for u in sudos) if sudos else "⚠️ No sudo users."
        await message.reply_text(text)

    @bot.on_message(filters.private & filters.command("gban"))
    async def gban_handler(_, message):
        if not owner_only(message.from_user.id):
            return await message.reply_text("❌ Not allowed.")
        if len(message.command) < 2:
            return await message.reply_text("Usage: /gban <user_id> [reason]")
        target_id = int(message.command[1])
        reason = " ".join(message.command[2:]) or "No reason"
        await add_gban(target_id, reason)
        await message.reply_text(f"✅ User `{target_id}` globally banned!\nReason: {reason}")

    @bot.on_message(filters.private & filters.command("gbanlist"))
    async def gbanlist_handler(_, message):
        if not owner_only(message.from_user.id):
            return await message.reply_text("❌ Not allowed.")
        gbans = await get_gban_list()
        text = "🚫 GBanned Users:\n" + "\n".join(f"{u['user_id']}: {u['reason']}" for u in gbans) if gbans else "⚠️ No GBanned users."
        await message.reply_text(text)

    @bot.on_callback_query()
    async def callback_handler(_, query):
        if not owner_only(query.from_user.id):
            return await query.answer("❌ Not allowed", show_alert=True)
        data = query.data
        if data == "control_panel":
            await query.message.edit_text("⚙️ Control Panel")
        elif data == "connected_bots":
            bots = await get_connected_bots()
            text = "🤖 Connected Bots:\n" + "\n".join(f"@{b['bot_username']}" for b in bots) if bots else "⚠️ No bots connected."
            await query.message.edit_text(text)


# ---------- Run Bot ----------
async def main():
    bot = GBANBot()
    register_handlers(bot)
    await bot.start()
    await idle()
    await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
