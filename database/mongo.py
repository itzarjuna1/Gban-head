from motor.motor_asyncio import AsyncIOMotorClient
import config

# Create Mongo client
client = AsyncIOMotorClient(config.MONGO_URI)

# Use the database specified in DB_NAME
db = client[config.DB_NAME]

print("[INFO] MongoDB connected to database:", config.DB_NAME)
