from fastapi import APIRouter, Depends
from services.post.create_post import create_new_post
from models.post import Post
from models.user import User
from schema.post import PostCreate
from utils.current_user import get_current_user

post_router = APIRouter(prefix="/api/v1", tags=["Post code snippet"])

@post_router.post("/posts")
async def new_post(post_data:PostCreate, 
                   user:User=Depends(get_current_user))->Post:
    
    return await create_new_post(post_data=post_data, 
                                 user=user)
