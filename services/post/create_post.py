from fastapi import HTTPException
import httpx
from dotenv import load_dotenv
import os
from models.user import User
from models.post import Post
from schema.post import PostCreate
load_dotenv()

AI_SERVER=os.getenv("AI_SERVER")

async def create_new_post(post_data:PostCreate,
                          user:User)->Post:
    """
    게시물 생성 후 포스팅
    포스팅 시 AI 서버에 정적 분석 및 이모지 할당 받아야 함
    AI 서버는 3 단계로 나누어 응답 -> saftey, warning, danger 
    saftey, warning 시에는 통과 -> 이모지 할당 받은 후 게시글 포스팅
    danger 시에는 불통
    Args:
    - post_data : PostCreate(title, description, code, language, tags)
    - user: user id, nickname 조회
    - vibe_emojis: AI 서버로부터 할당받은 emoji unicode list 
    Returns:
    - new_post: 작성된 게시글 
    """
    # STEP 1. POST user's code to AI Server for analyzing and matching vibe emojis
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=AI_SERVER,
                json={"code" : post_data.code},
                timeout=10.0
            )
            response.raise_for_status()
            ai_result = response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"AI Server is not responding: {e}"
        )
    # STEP 2. result including security level and vibe emojis unicode list
    security_level = ai_result.get("level", 1)
    vibe_emojis = ai_result.get("vibe_emojis", [])
    if security_level == 3:
        raise HTTPException(
            status_code=400,
            detail="This code is not allowed due to security policy"
        )
    new_post = Post(
        **post_data.model_dump(),
        authorId=user.id,
        authorNickname=user.nickname,
        authorProfileImage=user.profile_image_url,
        vibeEmojis=vibe_emojis,
        comments=[]
    )
    await new_post.create()
    
    return new_post