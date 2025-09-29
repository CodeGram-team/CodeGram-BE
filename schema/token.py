from pydantic import BaseModel
from typing import Optional

class TokenResponse(BaseModel):
    access_token:str
    refresh_token:str
    token_type:str="bearer"
    
class GoogleLoginResponse(BaseModel):
    status: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    signup_token: Optional[str] = None
    token_type: str = "bearer"