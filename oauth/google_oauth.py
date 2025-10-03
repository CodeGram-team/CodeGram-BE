from fastapi import HTTPException, status
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from dotenv import load_dotenv
import os
from models.user import User, SocialAccount 

load_dotenv()

GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID")

async def verify_google_id_token(token:str)->dict:
    """
    클라이언트로부터 받은 Google ID Token을 검증하고 사용자 정보 반환
    """
    try:
        # STEP 1. Google API 통해 ID Token 검증
        id_info = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )
        
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer')
        
        return {
            "id" : id_info.get("sub"),
            "email" : id_info.get("email"),
            "name" : id_info.get("name"),
            "picture" : id_info.get("picture")
        }
    except ValueError as ve:
        print(f"Google ID Token verification failed:{ve}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Google ID Token")

async def get_social_account(db:AsyncSession, 
                             provider:str, 
                             provider_user_id:str):
    """
    SocialAccount 테이블에서 특정 소셜 계정 정보 조회
    N+1 문제 방지 -> 연결된 User 정보도 함께 eager load
    Args:
    Returns:
    """
    query = select(SocialAccount).where(
        SocialAccount.provider == provider,
        SocialAccount.provider_user_id == provider_user_id
    ).options(selectinload(SocialAccount.user))
    
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_user_by_field(db:AsyncSession, 
                            field:str,
                            value:any):
    """
    특정 필드(email, nickname, id)로 사용자 정보 조회
    Args:
    Returns:
    """
    if not hasattr(User, field):
        raise ValueError(f"User model doesn't not have a field name '{field}'")
    
    column = getattr(User, field)
    query = select(User).where(column==value)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def create_user_with_social_account(db:AsyncSession,
                                          email:str,
                                          username:str,
                                          nickname:str,
                                          profile_image_url:str,
                                          provider:str,
                                          provideer_user_id:str)->User:
    """
    새로운 사용자와 소셜 계정 정보 동시 생성
    Args:
    Returns:
    """ 
    new_user = User(
        id=uuid.uuid4(),
        email=email,
        username=username,
        nickname=nickname,
        profile_image_url=profile_image_url
    )
    db.add(new_user)
    await db.flush()
    
    new_social_account = SocialAccount(
        user_id = new_user.id,
        provider=provider,
        provider_user_id=provideer_user_id
    )
    db.add(new_social_account)
    await db.commit()
    
    return new_user
    