import os
from dotenv import load_dotenv

load_dotenv()

# Telegram API
API_ID = int(os.getenv("API_ID", "34999060"))
API_HASH = os.getenv("API_HASH", "8a4b8206da5f273c4147a091a9e9c73f")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# MongoDB
MONGO_URI = os.getenv("MONGO_URI","")
DB_NAME = os.getenv("DB_NAME", "DARK_DATABASE")

# Owner
OWNER_ID = int(os.getenv("OWNER_ID", "7852340648"))

# Support & logging
SUPPORT_CHAT = os.getenv("SUPPORT_CHAT", "https://t.me/snowy_hometown")
GBAN_LOG_CHANNEL = int(os.getenv("GBAN_LOG_CHANNEL", "-1003583180037"))
GBAN_LOG_MEDIA = os.getenv("GBAN_LOG_MEDIA", "https://files.catbox.moe/5lkg94.mp4")
NETWORK_NAME = os.getenv("NETWORK_NAME", "DARK BOTS GBANS")
