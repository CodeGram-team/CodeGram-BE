from fastapi import APIRouter, Query, Depends, HTTPException, Response, Path
from typing import Optional, List
from beanie import PydanticObjectId
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from services.post.create_post import create_new_post
from services.post.get_post import get_feeds
from services.post.social_activity import toggle_like, leave_comment
from services.post.search_post import search_posts
from models.post import Post
from models.user import User
from schema.post import PostCreate, SortBy, CommentCreate, LikeResponse, PostResponse
from utils.current_user import get_current_user

post_router = APIRouter(prefix="/api/v1", tags=["Post code snippet"])

@post_router.post("/posts", response_model=PostResponse)
async def new_post(post_data:PostCreate, 
                   user:User=Depends(get_current_user))->Post:
    """
    Args:
    - post_data: PostCreate schema 
    - user: Request Header 'Authorization' : 'access token'
    Returns:
    - PostResponse: 
    """
    
    return await create_new_post(post_data=post_data, 
                                 user=user)
    
# @post_router.post("/posts", response_model=PostResponse)
# async def new_post(post_data:PostCreate)->PostResponse:
    
#     return await create_new_post(post_data=post_data)
    
@post_router.get("/feeds", response_model=List[Post])
async def get_post(current_user:User=Depends(get_current_user),
                   db:AsyncSession=Depends(get_db),
                   sort_by:SortBy=Query(default=SortBy.RECOMMENDED),
                   language:Optional[str]=Query(default=None),
                   page:int=Query(default=1, ge=1),
                   size:int=Query(default=10, ge=1, le=10)):
    
    skip = (page - 1) * size
    
    posts = await get_feeds(
        user_id=current_user.id,
        db=db,
        sort_by=sort_by,
        language=language,
        skip=skip,
        limit=size
    )
    return posts

@post_router.post("/likes/{post_id}", response_model=LikeResponse)
async def likes(post_id:PydanticObjectId=Path(...), 
                current_user:User=Depends(get_current_user)):
    """
    현재 인증된 사용자의 특정 게시물의 '좋아요' 상태 변경
    '좋아요' 상태가 아니면 -> '좋아요' 상태 변경
    '좋아요' 상태이면 -> '좋아요 취소' 상태 변경
    """
    updated_post, user_liked = await toggle_like(
        post_id=post_id,
        user_id=current_user.id
    )
    if not updated_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return LikeResponse(
        post_id=post_id,
        user_id=current_user.id,
        likes_count=updated_post.likesCount,
        user_has_liked=user_liked   
    )

@post_router.post("/comments/{post_id}", response_model=PostResponse)
async def comments(comment:CommentCreate, 
                   post_id:PydanticObjectId=Path(...), 
                   current_user:User=Depends(get_current_user)):
    result = await leave_comment(post_id=post_id, comment=comment, current_user=current_user)
    if result is None:
        raise HTTPException(status_code=404,
                            detail="Post ID not found")
    return result

@post_router.post("/search", response_model=List[Post])
async def search_post(
    vibe_emojis:Optional[List[str]]=Query(
        default=None, 
        alias="vibe_emoji", 
        description="Vibe Emojis는 하나 이상"),
    language:Optional[str]=Query(
        default=None,
        description="프로그래밍 언어(정확히 일치해야 함)"),
    tags:Optional[List[str]]=Query(
        default=None,
        alias="tag",
        description="태그 (하나 이상)"),
    text:Optional[str]=Query(
        default=None,
        alias="q",
        description="텍스트 검색(제목, 설명, 태그)"
    ),
    page:int=Query(default=1, ge=1),
    size:int=Query(default=10, ge=1, le=10)):
    """
    게시물 다중 조건 검색
    - 언어, 이모지, 태그, 텍스트 검색 가능
    """
    skip = (page -1) * size
    posts = await search_posts(
        language=language,
        vibe_emojis=vibe_emojis,
        tags=tags,
        text=text,
        skip=skip,
        limit=size
    )
    return posts

@post_router.delete("/{post_id}", status_code=204)
async def delete_post(post_id:PydanticObjectId,
                      current_user:User=Depends(get_current_user)):
    post = await Post.get(post_id)
    
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    
    if post.authorId == current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this post"
        )
    
    await post.delete()
    
    return Response(status_code=204)