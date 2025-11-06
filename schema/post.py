from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from enum import Enum
from uuid import UUID
from beanie import PydanticObjectId

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: PydanticObjectId = Field(..., alias="commentId")
    authorId: UUID
    authorNickname: str
    createdAt: datetime

class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    code: str = Field(..., min_length=1)
    language: str
    tags: Optional[List[str]] = []

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: PydanticObjectId = Field(..., alias="_id")
    authorId: UUID
    authorNickname: str
    authorProfileImageUrl: Optional[str] = None
    vibeEmojis: List[str] = []
    likesCount: int = 0
    comments: List[CommentResponse] = []
    createdAt: datetime

    class Config:
        populate_by_name = True # alias (_id)를 id로 매핑하기 위해 필요
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            PydanticObjectId:str
        }
        
class SortBy(str, Enum):
    RECOMMENDED = "recommended"
    LATEST = "latest"
    POPULAR = "popular"
    
class LikeResponse(BaseModel):
    post_id: PydanticObjectId
    user_id: UUID
    likes_count: int
    user_has_liked: bool