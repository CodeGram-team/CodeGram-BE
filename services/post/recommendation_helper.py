import numpy as np
from typing import List, Optional, Set
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.post import Like, Post 
from models.post_vector import PostVector
from beanie import PydanticObjectId

async def get_like_post_ids(user_id:UUID):
    """
    특정 사용자가 '좋아요'를 누른 모든 게시물의 ID Set을 반환
    """
    liked_posts = await Like.find(Like.user_id == user_id).to_list()
    
    return {str(post.post_id) for post in liked_posts}

async def get_user_profile_vector(user_id:UUID, 
                                  db:AsyncSession):
    """
    사용자가 좋아요 누른 게시물 벡터 평균 계산 -> '사용자 프로필 벡터' 반환
    """
    liked_post_ids = list(await get_like_post_ids(user_id=user_id))
    
    # 좋아요 기록이 없으면 벡터 프로필 생성 불가
    if not liked_post_ids:
        return None
    
    stmt = select(PostVector.vector).where(PostVector.post_id.in_(liked_post_ids))
    result = await db.execute(stmt)
    vectors = result.scalars().all() # List[List[float]]
    
    # 좋아요는 눌렀지만 아직 벡터화는 안 됨
    if not vectors:
        return None 
    
    profile_vector = np.mean(vectors, axis=0)
    return profile_vector

async def get_recommended_post_ids(profile_vector:np.ndarray,
                                   db:AsyncSession,
                                   exclude_ids:Set[str],
                                   language:Optional[str],
                                   skip:int,
                                   limit:int)->List[str]:
    """
    pgvector 사용해 프로필 벡터와 유사한 게시글 ID 목록 반환
    """
    query = select(PostVector.post_id)
    
    if language:
        query = query.where(PostVector.language == language)
    
    if exclude_ids:
        query = query.where(PostVector.post_id.notin_(list(exclude_ids)))
    
    # 코사인 거리 기준 정렬
    query = query.order_by(
        PostVector.vector.cosine_distance(profile_vector.tolist())
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    
    return result.scalars().all()