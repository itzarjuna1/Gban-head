from pyrogram import Client, filters, idle
import config

print("Starting bot...")

app = Client(
    "bot",
    api_id=int(config.API_ID),
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
)

@app.on_message(filters.private & filters.command("start"))
async def start_handler(_, message):
    await message.reply_text("✅ Bot is alive and responding!")

app.start()
print("Bot started successfully.")
idle()
