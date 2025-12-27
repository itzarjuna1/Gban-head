from pyrogram import Client
import config
from utils.language import lang


async def send_gban_log(app: Client, user_id: int, reason: str, origin: str, affected_chats: int = 0, is_unban: bool = False):
    """
    Sends a GBAN or UNGBAN log to the configured log channel.
    Includes media if GBAN_LOG_MEDIA is set.
    """
    action = "UnGBAN" if is_unban else "GBAN"
    caption = (
        f"🚫 **{action} LOG**\n\n"
        f"👤 User ID: `{user_id}`\n"
        f"📌 Reason: {reason}\n"
        f"🛠 Origin: {origin}\n"
        f"💬 Affected Chats: {affected_chats}\n"
    )

    try:
        if config.GBAN_LOG_MEDIA:
            await app.send_animation(
                chat_id=config.GBAN_LOG_CHANNEL,
                animation=config.GBAN_LOG_MEDIA,
                caption=caption
            )
        else:
            await app.send_message(
                chat_id=config.GBAN_LOG_CHANNEL,
                text=caption
            )
    except Exception as e:
        print(f"[WARN] Failed to send GBAN log: {e}")
