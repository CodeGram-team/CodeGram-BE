from pydantic import BaseModel, Field
from typing import Text, Optional
from enum import Enum

class DifficultyLevel(str, Enum):
    INTRODUCTORY = "introductory"
    COMPETITION = "competition"
    INTERVIEW = "interview"

class ChallengeBase(BaseModel):
    title:Text
    problem_id : int
    difficulty : Optional[DifficultyLevel] = None
    
    class Config:
        from_attributes : True
    
class ChallengeResponse(ChallengeBase):
    title:Text
    question : Text
    starter_code : Optional[str] = None
    url : Optional[str] = None

class ChallengeSubmissionRequest(BaseModel):
    language:str
    code:str

class ChallengeSubmissionResult(BaseModel):
    status:str
    failed_case:Optional[int] = Field(None)
    execution_time:Optional[float] = Field(None)
    message:Optional[str] = Field(None)

class ChallengeSubmissionResponse(BaseModel):
    submission_id:str
    result:ChallengeSubmissionResult