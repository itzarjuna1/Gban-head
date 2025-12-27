import asyncio
import os
import time

from pyrogram import Client
from pyrogram.errors import BadMsgNotification
import config
from database.mongo import db
from database.bots import register_bot

# ---------- Helper Functions ----------

async def ensure_time_sync():
    """
    Ensure the server time is in sync with Telegram.
    """
    now = int(time.time())
    print(f"[INFO] Current UNIX timestamp: {now}")
    await asyncio.sleep(1)  # small delay for stability

async def safe_start(app: Client):
    """
    Start the client safely, handling BadMsgNotification errors.
    """
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

# ---------- Main Bot ----------

async def main():
    # Ensure the sessions directory exists
    os.makedirs("./sessions", exist_ok=True)

    app = Client(
        "bot",
        api_id=int(config.API_ID),
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN,
        workdir="./sessions"  # use dedicated folder for sessions
    )

    # Safe start
    started = await safe_start(app)
    if not started:
        return

    # Register this bot in MongoDB
    me = await app.get_me()
    await register_bot(me.id, me.username)

    # Print bot info
    print(f"[INFO] Bot connected as @{me.username} ({me.id})")
    print("[INFO] MongoDB database:", config.DB_NAME)

    # Keep the bot running
    print("[INFO] Bot is running...")
    await asyncio.Event().wait()  # keeps bot alive

if __name__ == "__main__":
    asyncio.run(main())
