from pyrogram import Client, filters, idle
import config

app = Client(
    "gban_bot",
    api_id=int(config.API_ID),
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text("✅ Bot is alive and replying")

print("Starting bot...")
app.start()
print("Bot started. Listening for updates...")
idle()
