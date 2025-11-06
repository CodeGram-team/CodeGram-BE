from fastapi import HTTPException
import httpx
from dotenv import load_dotenv
import os
import json
from models.user import User
from models.post import Post
from schema.post import PostCreate
load_dotenv()

AI_SERVER=os.getenv("AI_SERVER")
ALLOWED_LANGUAGES = {"python", "c", "cpp", "nodejs", "java"}

async def create_new_post(post_data:PostCreate, user:User)->Post:
    """
    게시물 생성 후 포스팅
    포스팅 시 AI 서버에 정적 분석 및 이모지 할당 받아야 함
    AI 서버는 3 단계로 나누어 응답 -> allow, sandbox, block
    Args:
    - post_data : PostCreate(title, description, code, language, tags)
    - user: user id, nickname 조회
    Returns:
    - new_post: 작성된 게시글 
    """
    if post_data.language not in ALLOWED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported Language: {post_data.language}. Supported language are {list(ALLOWED_LANGUAGES)}" 
        )
    # STEP 1. [POST] user's code to AI Server for analyzing result and matching vibe emojis
    try:
        user_id = user.id
        nickname = user.nickname
        profile_url = user.profile_image_url
        req_data = {
            "code" : post_data.code,
            "language" : post_data.language
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=AI_SERVER,
                json=req_data,
                timeout=10.0
            )
            response.raise_for_status()
            response_text = response.content.decode('utf-8')
            ai_result = json.loads(response_text)
            print(f"AI Server response: {ai_result}")
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"AI Server is not responding: {e}"
        )
    # STEP 2. result including security level and vibe emojis unicode list
    """
    ai_result: 
    """
    decision = ai_result.get("decision") # allow | sandbox | block
    vibe_emojis = ai_result.get("emojis", [])
    
    if decision == "block":
        reasons = ai_result.get("reasons", [])
        block_reason_detail = {
            "code" : "CODE_REJECTED",
            "message" : "This code is not allowed due to security policy.",
            "reasons" : reasons
        }
        raise HTTPException(
            status_code=400,
            detail=block_reason_detail
        )
    new_post = Post(
        **post_data.model_dump(),
        authorId=user_id,
        authorNickname=nickname,
        authorProfileImageUrl=profile_url,
        vibeEmojis=vibe_emojis,
        comments=[]
    )
    await new_post.create()
    
    return new_post