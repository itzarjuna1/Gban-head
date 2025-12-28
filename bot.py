import asyncio
import signal
import sys
from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import config
from database.mongo import db
from database.bots import register_bot, get_connected_bots
from database.sudo import add_sudo, remove_sudo, get_sudo_list
from database.gbans import add_gban, get_gban_list

from ..logging import LOGGER

# ------------------ Bot Class ------------------
class GbanHead(Client):
    def __init__(self):
        LOGGER(__name__).info("Starting GbanHead Bot...")
        super().__init__(
            name="Gban-head",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            parse_mode=ParseMode.HTML,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.username = me.username
        self.id = me.id
        self.name = me.first_name + " " + (me.last_name or "")
        self.mention = me.mention

        # Send start message to LOG_GROUP_ID
        if config.LOG_GROUP_ID:
            button = InlineKeyboardMarkup(
                [[InlineKeyboardButton("Add Me To Group", url=f"https://t.me/{self.username}?startgroup=true")]]
            )
            try:
                await self.send_message(
                    chat_id=config.LOG_GROUP_ID,
                    text=f"✅ Bot Started!\nName: {self.name}\nID: {self.id}\nUsername: @{self.username}",
                    reply_markup=button,
                )
            except errors.ChatWriteForbidden:
                LOGGER(__name__).error("Cannot write to log group. Check permissions.")

        # Check admin status in log group
        if config.LOG_GROUP_ID:
            try:
                chat_member = await self.get_chat_member(config.LOG_GROUP_ID, self.id)
                if chat_member.status != ChatMemberStatus.ADMINISTRATOR:
                    LOGGER(__name__).error("Promote bot as admin in the log group!")
            except Exception as e:
                LOGGER(__name__).error(f"Error checking admin status: {e}")

        LOGGER(__name__).info(f"GbanHead Bot Started as {self.name}")

    async def stop(self):
        LOGGER(__name__).info("Stopping GbanHead Bot...")
        await super().stop()
        LOGGER(__name__).info("Bot stopped successfully.")

# ------------------ Initialize Bot ------------------
app = GbanHead()

# ------------------ Example Command ------------------
@app.on_message(filters.private & filters.command("start"))
async def start_handler(client, message):
    await message.reply_text(f"✅ Hello! I am {app.name}.")

# ------------------ Graceful Shutdown ------------------
def shutdown(signal_num, frame):
    LOGGER(__name__).info("Caught exit signal. Shutting down...")
    asyncio.get_event_loop().create_task(app.stop())
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

# ------------------ Run ------------------
async def main():
    # Ensure sessions folder exists
    import os
    os.makedirs("./sessions", exist_ok=True)

    await app.start()
    # Register bot in MongoDB
    me = await app.get_me()
    await register_bot(me.id, me.username)
    LOGGER(__name__).info(f"Bot connected as @{me.username} ({me.id})")
    LOGGER(__name__).info(f"MongoDB database: {config.DB_NAME}")
    LOGGER(__name__).info("Bot is running... Press Ctrl+C to stop.")

    # Keep bot running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
