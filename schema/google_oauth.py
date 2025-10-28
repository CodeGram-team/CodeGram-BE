from pydantic import BaseModel, field_validator
import re

class GoogleLoginRequest(BaseModel):
    id_token:str
    
class SignUpCompletionRequest(BaseModel):
    signup_token: str
    nickname: str

    @field_validator('nickname')
    def nickname_valid(cls, v):
        if not 3 <= len(v) <= 10:
            raise ValueError("닉네임은 3~10자리여야 합니다")
        if not re.match(r'^[가-힣a-zA-Z0-9_]+$', v):
            raise ValueError("닉네임은 한글, 영어, 숫자, _만 허용됩니다")
        return v