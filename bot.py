import asyncio
from pyrogram import Client, idle

import config
from database.bots import register_bot
from utils.gban_watcher import start_gban_watcher

app = Client(
    "gban_network",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    plugins=dict(root="plugins")
)

async def main():
    await app.start()

    me = await app.get_me()
    print(f"[INFO] Logged in as @{me.username} ({me.id})")

    # Register this bot in MongoDB
    await register_bot(app)

    # Start global ban watcher (Mongo stream)
    asyncio.create_task(start_gban_watcher(app))

    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
