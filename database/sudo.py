from database.mongo import db

sudo_col = db.sudo_users


async def add_sudo(user_id: int):
    await sudo_col.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )


async def remove_sudo(user_id: int):
    await sudo_col.delete_one({"user_id": user_id})


async def get_sudo_list():
    sudos = []
    async for user in sudo_col.find({}):
        sudos.append(user["user_id"])
    return sudos


async def is_sudo(user_id: int) -> bool:
    return await sudo_col.find_one({"user_id": user_id}) is not None    
