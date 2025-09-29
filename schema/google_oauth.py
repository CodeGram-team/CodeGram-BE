from pydantic import BaseModel

class GoogleLoginRequest(BaseModel):
    id_token:str
    
class SignUpCompletionRequest(BaseModel):
    signup_token:str
    nickname:str