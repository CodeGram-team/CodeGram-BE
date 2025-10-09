import uvicorn 
from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.mongodb import connect_to_mongo, close_mongo_connection
from db.rmq import rmq_client
from api.v1.auth import oauth_router
from api.v1.execution import execution_router

async def start():
    await connect_to_mongo()
    await rmq_client.connect()
    print("Application startup complete")
    
async def shutdown():
    await close_mongo_connection()
    await rmq_client.close()
    print("Application shutdown")
    
@asynccontextmanager
async def lifespan(app:FastAPI):
    await start()
    yield
    await shutdown()

app = FastAPI(title="CodeGram API",
              description="API for CodeGram Service",
              lifespan=lifespan)


app.include_router(oauth_router)
app.include_router(execution_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)