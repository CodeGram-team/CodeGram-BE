from pydantic import BaseModel,Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List
from beanie import PydanticObjectId

class ProfilePost(BaseModel):
    id: PydanticObjectId = Field(..., alias="_id")
    title: str
    language:str
    likesCount:int = 0
    createdAt: datetime
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {PydanticObjectId:str}

class UserProfileResponse(BaseModel):
    id: UUID
    nickname : str
    username : str
    profile_image_url : Optional[str] = None
    created_at : datetime
    
    posts : List[ProfilePost]
    
    class Config:
        from_attributes = True
        json_encoders = {UUID:str}