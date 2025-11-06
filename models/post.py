from beanie import Document, PydanticObjectId, Indexed
from pymongo import IndexModel
from pydantic import Field, BaseModel
from datetime import datetime, timezone
from typing import List, Optional, Annotated
from uuid import UUID

class Comment(BaseModel):
    commentId: PydanticObjectId = Field(default_factory=PydanticObjectId)
    authorId: UUID
    authorNickname: str
    content:str
    createdAt: datetime=Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # ObjectId 타입 에러 해결
    model_config = {
        "arbitrary_types_allowed" : True   
    }

class Post(Document):
    # Author Information
    authorId: UUID
    authorNickname:str
    authorProfileImageUrl:Optional[str] = None
    # Post Information
    title:str = Field(..., min_length=1, max_length=100)
    description:Optional[str] = None
    code:str = Field(..., min_length=1)
    language:str
    # Metadata & social function
    tags: List[str] = []
    vibeEmojis : List[str] = []
    likesCount:int = 0
    # Embedded document
    comments: List[Comment]
    # Timestamp
    createdAt: datetime=Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        # MongoDB Collection name
        name = "posts" 
        
class Like(Document):
    user_id: Annotated[UUID, Indexed()] = Field(alias="userId")
    post_id: Annotated[PydanticObjectId, Indexed()] = Field(alias="postId")
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "likes"
        indexes = [
            IndexModel([("userId",1),("postId",1)], unique=True)
        ]
        populate_by_name=True