import uvicorn 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from db.mongodb import init_db, close_connection
from db.rmq import rmq_client
from api.v1.auth import oauth_router
from api.v1.execution import execution_router
from api.v1.post import post_router
from api.v1.challenge import challenge_router
from api.v1.profile import profile_router

async def start():
    await init_db()
    await rmq_client.connect()
    print("Application startup complete")
    
async def shutdown():
    await close_connection()
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

origins = [
    "https://codesns.cloudjin.kr" # 나중에 실제 배포될 프론트엔드 주소
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # ["*"] 대신 명시적인 리스트 사용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(oauth_router)
app.include_router(execution_router)
app.include_router(post_router)
app.include_router(challenge_router)
app.include_router(profile_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)