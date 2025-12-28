import asyncio
from pyrogram import Client, filters, idle
import config

app = Client(
    "bot",
    api_id=int(config.API_ID),
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    workers=1
)

# ---------- Command Handlers ----------
@app.on_message(filters.private & filters.command("start"))
async def start(_, message):
    await message.reply_text("✅ Bot is alive and responding!")

@app.on_message(filters.private & filters.command("ping"))
async def ping(_, message):
    await message.reply_text("🏓 Pong!")

# ---------- Main ----------
async def main():
    await app.start()
    print("✅ Bot started and listening...")
    await idle()  # Keeps the bot alive and processing updates
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
