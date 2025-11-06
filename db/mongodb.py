from pymongo import AsyncMongoClient
from beanie import init_beanie
from dotenv import load_dotenv
import os
from models.post import Post, Like

load_dotenv()
MONGODB_URL=os.getenv("MONGODB_URL")

class DBMongo:
    client : AsyncMongoClient = None
    db = None
    
db_client = DBMongo()

async def init_db():
    try:
        
        db_client.client = AsyncMongoClient(MONGODB_URL)
        db_client.db = db_client.client.get_database("codegram")
        await db_client.client.server_info()
        await init_beanie(database=db_client.db, document_models=[Post, Like])
        print("MongoDB Connection success")
        
    except Exception as e:
        print(f"MongoDB Connection failed: {e}")

async def close_connection():
    print("Closing MongoDB connection")
    if db_client.client:
        await db_client.client.close()
        print("MongoDB connetion closed")