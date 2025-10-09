from beanie import Document
from pydantic import Field, BaseModel
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from bson import ObjectId

class Comment(BaseModel):
    commentId: ObjectId = Field(default_factory=ObjectId)
    authorId: UUID
    authorNickname: str
    content:str
    createdAt: datetime=Field(default_factory=lambda: datetime.now(timezone.utc))

class Post(Document):
    # Author Information
    authorId: UUID
    authorNickname:str
    authorProfileImage:Optional[str] = None
    # Post Information
    title:str = Field(..., min_length=1, max_length=100)
    description:Optional[str] = None
    code:str = Field(..., min_length=1)
    language:str
    # Metadata & social function
    tags: List[str] = []
    vibeEmojis : List[str] = []
    likeCount:int = 0
    # Embedded document
    comments: List[Comment]
    # Timestamp
    createdAt: datetime=Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        # MongoDB Collection name
        name = "posts" 