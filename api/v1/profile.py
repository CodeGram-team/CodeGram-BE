from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from db.database import get_db
from oauth.google_oauth import get_user_by_field
from services.post.get_post import get_posts_by_author_id
from schema.user import UserProfileResponse

profile_router = APIRouter(prefix="/api/v1", tags=["User Profile Lookup"])

@profile_router.get("/profile/{nickname}", response_model=UserProfileResponse)
async def get_user_profile(nickname:str=Path(...), 
                           db:AsyncSession=Depends(get_db)):
    user = await get_user_by_field(db=db, field="nickname", value=nickname)
    
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    user_posts = await get_posts_by_author_id(author_id=user.id)
    
    user_data_dict = user.__dict__
    
    posts_as_dict = [post.model_dump(by_alias=True) for post in user_posts]
    
    response_data = {
        **user_data_dict,
        "posts" : posts_as_dict
    }
    
    return UserProfileResponse(**response_data)

