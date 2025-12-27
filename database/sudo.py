from database.mongo import db
import config

sudo_col = db.sudo_users


async def ensure_owner():
    """
    Ensure OWNER_ID is always sudo
    """
    await sudo_col.update_one(
        {"user_id": config.OWNER_ID},
        {
            "$set": {
                "user_id": config.OWNER_ID,
                "is_owner": True
            }
        },
        upsert=True
    )


async def add_sudo(user_id: int):
    await sudo_col.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "user_id": user_id,
                "is_owner": False
            }
        },
        upsert=True
    )


async def del_sudo(user_id: int):
    if user_id == config.OWNER_ID:
        return False  # owner cannot be removed
    await sudo_col.delete_one({"user_id": user_id})
    return True


async def is_sudo(user_id: int) -> bool:
    user = await sudo_col.find_one({"user_id": user_id})
    return bool(user)


async def get_sudo_list():
    users = []
    async for u in sudo_col.find():
        users.append(u)
    return users
