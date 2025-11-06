from fastapi import HTTPException
from typing import Optional, List
from uuid import UUID
from beanie import PydanticObjectId
from sqlalchemy.ext.asyncio import AsyncSession
from services.post.recommendation_helper import get_like_post_ids,get_recommended_post_ids,get_user_profile_vector
from models.post import Post
from models.post_vector import PostVector
from schema.post import PostResponse

"""
게시글 조회(인스타그램 피드 형식)
최신순, 좋아요 많은 순, 언어 종류 카테고리가 존재하여 조회할 수 있어야 함
페이지네이션을 적용하여 최적으로 데이터 처리할 수 있게 해야 함
"""

async def get_posts(*, 
                    language:Optional[str]=None,
                    sort_by:str="latest",
                    skip:int = 0,
                    limit:int = 10) -> List[Post]:
    """
    조건에 따라 게시물을 조회하고 페이지네이션을 적용
    Args:
    - language: 필터링할 프로그래밍 언어(python, java, c, c++, nodejs, html)
    - sort_by: 정렬 기준 ("latest" or "popular")
    - skip: 건너뛸 게시글 수
    - limit: 반환할 게시글 최대 수 (페이지네이션)
    Returns:
    - List[Post]: 조회된 Beanie Post 모델 객체 리스트
    """
    # STEP 1. Dynamic query setting
    query = {}
    if language:
        query["language"] = language
    
    # STEP 2. Beanie Query start
    post_query = Post.find(query)
    
    # STEP 3 .Sorting option setting
    if sort_by == "popular":
        post_query = post_query.sort(-Post.likesCount)
    else:
        post_query = post_query.sort(-Post.createdAt)
    
    # STEP 4. Pagination and query execute
    posts = await post_query.skip(skip).limit(limit).to_list()
    
    return posts

async def get_posts_by_author_id(author_id:UUID)->List[Post]:
    return await Post.find(Post.authorId == author_id).sort(-Post.createdAt).to_list()

async def get_feeds(*,
                    user_id:UUID,
                    db:AsyncSession,
                    language:Optional[str]=None,
                    sort_by:str="recommended",
                    skip:int=0,
                    limit:int=10)->List[Post]:
    """
    사용자에게 맞춤형 또는 일반 게시물 피드 반환
    """
    if sort_by in ("latest", "popular"):
        return await get_posts(
            language=language, 
            sort_by=sort_by, 
            skip=skip, 
            limit=limit
        )

    profile_vector = await get_user_profile_vector(user_id, db)
    
    recommended_post_ids: List[str] = []

    if profile_vector is not None:
        liked_post_ids = await get_like_post_ids(user_id)
        
        recommended_post_ids = await get_recommended_post_ids(
            profile_vector=profile_vector,
            db=db,
            exclude_ids=liked_post_ids,
            language=language,
            skip=skip,
            limit=limit
        )
    
    if recommended_post_ids:
        
        object_ids = [PydanticObjectId(pid) for pid in recommended_post_ids]
        posts_map = {
            str(p.id): p 
            for p in await Post.find({"_id": {"$in": object_ids}}).to_list()
        }
        
        sorted_posts = [
            posts_map[pid] 
            for pid in recommended_post_ids 
            if pid in posts_map
        ]
        
        return sorted_posts
        
    else:
        return await get_posts(
            language=language,
            sort_by="latest", 
            skip=skip,
            limit=limit
        )