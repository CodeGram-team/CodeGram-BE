from fastapi import APIRouter, HTTPException, status, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from datetime import timedelta
from db.database import get_db
from db.redis import get_redis_client
from schema.google_oauth import GoogleLoginRequest, SignUpCompletionRequest
from schema.token import TokenResponse, GoogleLoginResponse
from oauth.google_oauth import get_social_account, get_user_by_field, verify_google_id_token, create_user_with_social_account
from core.token import Token
from models.user import User
from utils.current_user import get_current_user, oauth2_scheme

oauth_router = APIRouter(prefix="/api/v1", tags=["OAuth 2.0 Authentication"])
token_instance = Token()

async def handle_login_success(user:User, redis:Redis) -> TokenResponse:
    """
    로그인 및 회원가입 성공 시 토큰 생성 및 Redis 저장 처리 
    """
    access_token = token_instance.create_access_token(data={"sub" : str(user.id)})
    refresh_token = token_instance.create_refresh_token(data={"sub":str(user.id)})
    ttl = timedelta(days=token_instance.REFRESH_TOKEN_EXPIRE_DAYS)
    await redis.setex(
        f"refresh_token:{user.id}",
        ttl,
        refresh_token
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@oauth_router.post("/google/auth", response_model=GoogleLoginResponse)
async def google_auth(request:GoogleLoginRequest,
                      db:AsyncSession=Depends(get_db),
                      redis:Redis=Depends(get_redis_client)):
    
    # STEP 1. Google Code를 사용하여 인증 처리
    user_info = await verify_google_id_token(request.id_token)
    provider = "google"
    provider_user_id = user_info["id"]
    
    social_account = await get_social_account(db=db, provider=provider, provider_user_id=provider_user_id)
    
    if social_account:
        # -- Login 처리 --
        user = social_account.user
        token_data = await handle_login_success(user, redis)
        return GoogleLoginResponse(
            status="login",
            access_token=token_data.access_token,
            refresh_token=token_data.refresh_token
        )
    else:
        # -- Singup 처리 --
        if await get_user_by_field(db=db, field="email", value=user_info["email"]):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Email is already registered")
        signup_data = {
            "provider" : provider, 
            "provider_user_id" : provider_user_id,
            "email" : user_info["email"],
            "username" : user_info.get("name"),
            "profile_image_url" : user_info.get("picture")
        }
        singup_token = token_instance.create_signup_token(data=signup_data)
        return GoogleLoginResponse(
            status="signup",
            signup_token=singup_token
        )

@oauth_router.post("/google/signup", response_model=TokenResponse)
async def google_complete_signup(
    request: SignUpCompletionRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis_client)
):
    """2단계: Signup Token과 닉네임으로 최종 회원가입을 완료합니다."""
    signup_data = token_instance.verify_signup_token(request.signup_token)

    if await get_user_by_field(db, field="nickname", value=request.nickname):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nickname is already taken.")

    user = await create_user_with_social_account(
        db=db,
        email=signup_data["email"],
        username=signup_data["username"],
        nickname=request.nickname,
        profile_image_url=signup_data.get("profile_image_url"),
        provider=signup_data["provider"],
        provider_user_id=signup_data["provider_user_id"]
    )

    return await handle_login_success(user, redis)

@oauth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user:User=Depends(get_current_user),
                 token:str=Depends(oauth2_scheme),
                 redis:Redis=Depends(get_redis_client)):
    """
    사용자 로그아웃 처리
    - Refresh Token 삭제 및 Access Token Blacklist로 관리
    """
    await redis.delete(f"refresh_token:{current_user.id}")
    
    await token_instance.blacklist_token(token=token, redis=redis)
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)