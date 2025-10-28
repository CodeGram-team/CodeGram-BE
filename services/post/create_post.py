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

async def create_new_post(post_data:PostCreate, user:User)->Post:
    """
    게시물 생성 후 포스팅
    포스팅 시 AI 서버에 정적 분석 및 이모지 할당 받아야 함
    AI 서버는 3 단계로 나누어 응답 -> saftey, warning, danger 
    saftey, warning 시에는 통과 -> 이모지 할당 받은 후 게시글 포스팅
    danger 시에는 불통
    Args:
    - post_data : PostCreate(title, description, code, language, tags)
    - user: user id, nickname 조회
    Returns:
    - new_post: 작성된 게시글 
    """
    # STEP 1. [POST] user's code to AI Server for analyzing result and matching vibe emojis
    try:
        user_id = user.id
        nickname = user.nickname
        profile_url = user.profile_image_url
        # user_id = '5082d4f9-59ac-4ac8-90c2-be5a1bc1073a'
        # nickname = 'ㄹㅎ'
        # user_profile = 'https://lh3.googleusercontent.com/a/ACg8ocJ0prZA199gyifDp2grbuGoCHqHrQmMmL-iAVaFgMETs-T1KQ=s96-c'
        req_data = {
            "lanuage" : post_data.language,
            "code" : post_data.code,
            "meta" : {
                "filename" : None,
                "author_id" : user_id,
                "client_version" : None
            }
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
    is_safe = ai_result.get("safe")
    #risk_score = ai_result.get("risk_score", 0)
    vibe_emojis = ai_result.get("emojis", [])
    if not is_safe:
        raise HTTPException(
            status_code=400,
            detail="This code is not allowed due to security policy"
        )
    new_post = Post(
        **post_data.model_dump(),
        authorId=user_id,
        authorNickname=nickname,
        authorProfileImage=profile_url,
        vibeEmojis=vibe_emojis,
        comments=[]
    )
    await new_post.create()
    
    return new_post