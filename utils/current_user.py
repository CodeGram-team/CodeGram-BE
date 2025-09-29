from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError
from redis.asyncio import Redis
from core.token import Token
from db.database import get_db
from db.redis import get_redis_client
from oauth.google_oauth import get_user_by_field
from models.user import User

token_instance = Token()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/google")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    redis: Redis = Depends(get_redis_client),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Access Token 검증, 유효하다면 DB에서 해당 사용자 정보 반환
    API 엔드포인트에서 사용자 인증에 사용하는 의존성 함수
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    is_blacklisted = await redis.get(f"blacklist:{token}")
    if is_blacklisted:
        raise credentials_exception

    try:
        payload = token_instance.verify_token(token=token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_by_field(db=db, field="id", value=user_id)
    if user is None:
        raise credentials_exception

    return user