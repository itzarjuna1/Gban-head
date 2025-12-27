from motor.motor_asyncio import AsyncIOMotorClient
import config

# Create Mongo client
client = AsyncIOMotorClient(config.MONGO_URI)

# Use the database specified in DB_NAME
db = client[config.DARK_DATABASE]

print("[INFO] MongoDB connected to database:", config.DARK_DATABASE)
