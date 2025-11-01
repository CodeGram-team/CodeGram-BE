from jose import jwt, JWTError
from datetime import timedelta, timezone, datetime
from redis.asyncio import Redis
from dotenv import load_dotenv
import os

load_dotenv()

class Token:
    def __init__(self):
        self.ACCESS_TOKEN_KEY=os.getenv("ACCESS_TOKEN_KEY")
        self.REFRESH_TOKEN_KEY=os.getenv("REFRESH_TOKEN_KEY")
        self.SIGNUP_KEY=os.getenv("SIGNUP_KEY")
        self.ALGORITHM=os.getenv("ALGORITHM")
        if not all([self.ACCESS_TOKEN_KEY, self.REFRESH_TOKEN_KEY, self.SIGNUP_KEY]):
            raise ValueError("One or more JWT secret keys are missing from the environment variables")
        self.ACCESS_EXPIRE_MINUTES=int(os.getenv("ACCESS_EXPIRE_MINUTES", "30"))
        self.REFRESH_TOKEN_EXPIRE_DAYS=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "180"))
        
    def create_access_token(self, data:dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.ACCESS_EXPIRE_MINUTES)
        expires_time = int(expire.timestamp())
        to_encode.update({"exp" : expire})
        encoded_jwt = jwt.encode(to_encode, self.ACCESS_TOKEN_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt, expires_time
        
    def create_refresh_token(self, data:dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp" : expire})
        return jwt.encode(to_encode, self.REFRESH_TOKEN_KEY, algorithm=self.ALGORITHM)
        
    def create_signup_token(self, data:dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=10)
        to_encode.update({"exp" : expire})
        return jwt.encode(to_encode, self.SIGNUP_KEY, algorithm=self.ALGORITHM)
    
    def verify_token(self, token:str, is_refresh:bool=False):
        try:
            secret_key = self.REFRESH_TOKEN_KEY if is_refresh else self.ACCESS_TOKEN_KEY
            payload = jwt.decode(token, secret_key, algorithms=[self.ALGORITHM])
            return payload
        except JWTError as je:
            raise je
        
    def verify_signup_token(self, token):
        try:
            secret_key = self.SIGNUP_KEY
            payload = jwt.decode(token, secret_key, algorithms=[self.ALGORITHM])
            return payload
        except JWTError as je:
            raise je
        
    async def blacklist_token(self, token:str, redis:Redis):
        try:
            payload = jwt.decode(token, 
                                 self.ACCESS_TOKEN_KEY, 
                                 algorithms=[self.ALGORITHM],
                                 options={"verify_exp" : False})
            expire_time = payload.get("exp")
            if not expire_time:
                return 
            time_now = datetime.now(timezone.utc)
            time_to_expire = datetime.fromtimestamp(expire_time, tz=timezone.utc) - time_now
            
            if time_to_expire.total_seconds() > 0:
                await redis.setex(
                    f"blacklist:{token}",
                    int(time_to_expire.total_seconds()),
                    "true"
                )
        except Exception: # 토큰 디코딩 실패해도 로그아웃 자체는 막지 않음
            pass
            