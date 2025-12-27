from database.mongo import db

async def create_indexes():
    # GBAN users
    await db.gbans.create_index("user_id", unique=True)
    
    # Sudo users
    await db.sudo_users.create_index("user_id", unique=True)
    
    # Served chats
    await db.served_chats.create_index("chat_id", unique=True)
    
    # Connected bots
    await db.connected_bots.create_index("bot_id", unique=True)

    print("[INFO] MongoDB indexes created successfully")
