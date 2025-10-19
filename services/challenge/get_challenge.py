from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from models.challenge import Challenge

async def get_challenges(db:AsyncSession,
                         difficulty:Optional[str]=None,
                         skip:int = 0,
                         limit:int = 20
                         )->List[Challenge]:
    """
    조건에 따라 챌린지 문제 목록 조회 및 페이지네이션 
    Args:
    - db: SQLAlchemy 비동기 세션
    - difficulty: 챌린지 난이도(interview, competion, introductory)
    - skip: 건너뛸 레코드 수 (페이지네이션 offset)
    - limit: 반환할 레코드 수
    Returns:
    - Challenge: 조회된 Challenge SQLAlchemy 모델 객체 리스트
    """
    query = select(Challenge)
    
    # 난이도 필터링
    if difficulty:
        query = query.where(Challenge.difficulty == difficulty)
    
    query = query.order_by(Challenge.id).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_challenge_by_id(db:AsyncSession, 
                              problem_id:int)-> Optional[Challenge]:
    """
    problem id를 기반으로 특정 챌린지 문제 상세 조회
    Args:
    - db: SQLAlchemy 비동기 세션
    - problem_id: 조회할 문제의 ID
    Returns:
    - Challenge: 조회된 Challenge 모델 객체, 해당 ID의 문제가 없으면 None을 반환
    """
    query = select(Challenge).where(Challenge.problem_id == problem_id)
    result = await db.execute(query)
    
    return result.scalar_one_or_none()