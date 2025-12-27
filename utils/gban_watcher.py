import asyncio
from database.gbans import is_gbanned
from utils.gban_logger import send_gban_log
from database.mongo import db

gbans_col = db.gbans


async def start_gban_watcher(app):
    """
    Watches MongoDB gbans collection.
    Any new gban triggers ban on this bot.
    """
    await asyncio.sleep(2)  # allow startup to settle

    async with gbans_col.watch() as stream:
        async for change in stream:
            if change["operationType"] not in ("insert", "update"):
                continue

            doc = change.get("fullDocument")
            if not doc or not doc.get("active"):
                continue

            user_id = doc["user_id"]
            reason = doc.get("reason", "Global Ban")

            await execute_gban(app, user_id, reason)


async def execute_gban(app, user_id: int, reason: str):
    from database.chats import get_served_chats

    chats = await get_served_chats()
    affected = 0

    for chat_id in chats:
        try:
            await app.ban_chat_member(chat_id, user_id)
            affected += 1
        except:
            pass

    await send_gban_log(
        app=app,
        user_id=user_id,
        reason=reason,
        origin="MongoDB Sync",
        affected_chats=affected,
        is_unban=False
    )
