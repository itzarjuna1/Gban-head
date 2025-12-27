from database.mongo import db

# Collection for connected bots
bots_col = db.connected_bots


async def register_bot(bot_id: int, bot_username: str):
    """
    Register a bot in the network.
    If the bot already exists, update its username.
    """
    await bots_col.update_one(
        {"bot_id": bot_id},
        {"$set": {"bot_username": bot_username}},
        upsert=True
    )


async def remove_bot(bot_id: int):
    """
    Remove a bot from the network.
    """
    await bots_col.delete_one({"bot_id": bot_id})


async def get_connected_bots():
    """
    Return a list of all connected bots in the network.
    """
    bots = []
    async for b in bots_col.find():
        bots.append({
            "bot_id": b.get("bot_id"),
            "bot_username": b.get("bot_username")
        })
    return bots
