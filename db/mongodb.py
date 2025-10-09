from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from dotenv import load_dotenv
import os
load_dotenv()

MONGODB_URL=os.getenv("MONGODB_URL")
class DBMongo:
    client : AsyncMongoClient = None
    db : AsyncDatabase = None
    
db_client = DBMongo()

async def connect_to_mongo():
    """
    Connect MongoDB when start application
    """
    db_client.client = AsyncMongoClient(MONGODB_URL)
    db_client.db = db_client.client.get_database("codegram")
    
    try:
        await db_client.client.server_info()
        print("MongoDB connection success")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")

async def close_mongo_connection():
    print("Close MongoDB..")
    if db_client.client:
        await db_client.client.close()

async def get_mongo():
    if db_client.db is None:
        raise Exception("MongoDB is not connected")
    return db_client.db
        