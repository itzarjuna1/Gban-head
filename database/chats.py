from database.mongo import db

chats_col = db.served_chats


async def add_chat(chat_id: int):
    await chats_col.update_one(
        {"chat_id": chat_id},
        {"$set": {"chat_id": chat_id}},
        upsert=True
    )


async def remove_chat(chat_id: int):
    await chats_col.delete_one({"chat_id": chat_id})


async def get_served_chats():
    chats = []
    async for c in chats_col.find():
        chats.append(c["chat_id"])
    return chats
