from pydantic import BaseModel
from typing import Optional

class TokenResponse(BaseModel):
    access_token:str
    refresh_token:str
    expires_time: int
    token_type:str="bearer"
    
class GoogleLoginResponse(BaseModel):
    status: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    signup_token: Optional[str] = None
    expires_time: Optional[int] = None
    token_type: str = "bearer"
    
class RefreshTokenRequest(BaseModel):
    refresh_token:str