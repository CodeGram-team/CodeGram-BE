from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.post import Post
from models.user import User

async def lookup_profile(db:AsyncSession, 
                         user_id:str):
    
    query = select(User).where(User.id==user_id)
    