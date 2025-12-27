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
    Retry pinging Telegram if BadMsgNotification occurs.
    """
    now = int(time.time())
    print(f"[INFO] Current UNIX timestamp: {now}")
    # Sleep a little to let time stabilize
    await asyncio.sleep(1)

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

    # Optional: register this bot in MongoDB
    await register_bot(bot_id=(await app.get_me()).id, bot_username=(await app.get_me()).username)

    # Keep the bot running
    print("[INFO] Bot is running...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
