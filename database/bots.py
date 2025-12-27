import time
from database.mongo import db

bots_col = db.connected_bots


async def register_bot(app):
    """
    Register or update this bot in MongoDB
    """
    me = await app.get_me()

    await bots_col.update_one(
        {"bot_id": me.id},
        {
            "$set": {
                "bot_id": me.id,
                "bot_username": me.username,
                "bot_name": me.first_name,
                "connected_at": int(time.time())
            }
        },
        upsert=True
    )


async def get_connected_bots():
    """
    Return list of all connected bots
    """
    bots = []
    async for bot in bots_col.find():
        bots.append(bot)
    return bots
