import uvicorn 
from fastapi import FastAPI
from api.v1.auth import oauth_router

app = FastAPI()
app.include_router(oauth_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)