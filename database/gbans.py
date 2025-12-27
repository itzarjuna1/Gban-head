import time
from database.mongo import db

gbans_col = db.gbans


async def add_gban(user_id: int, reason: str, by: int):
    """
    Add a user to global ban list
    """
    await gbans_col.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "user_id": user_id,
                "reason": reason,
                "by": by,
                "timestamp": int(time.time()),
                "active": True
            }
        },
        upsert=True
    )


async def remove_gban(user_id: int):
    """
    Remove user from global ban
    """
    await gbans_col.update_one(
        {"user_id": user_id},
        {"$set": {"active": False}}
    )


async def is_gbanned(user_id: int) -> bool:
    gban = await gbans_col.find_one(
        {"user_id": user_id, "active": True}
    )
    return bool(gban)


async def get_gban_list():
    users = []
    async for u in gbans_col.find({"active": True}):
        users.append(u)
    return users
