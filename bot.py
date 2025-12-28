import asyncio
from pyrogram import Client, filters
import config

app = Client(
    name="bot",
    api_id=int(config.API_ID),
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
)

@app.on_message(filters.private & filters.command("start"))
async def start_handler(_, message):
    await message.reply_text("✅ Bot is alive and responding!")

async def main():
    await app.start()
    print("✅ Bot started successfully")
    await asyncio.Event().wait()  # keep alive

if __name__ == "__main__":
    asyncio.run(main())
