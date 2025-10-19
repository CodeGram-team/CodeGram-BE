from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from db.database import get_db
from services.challenge.get_challenge import get_challenge_by_id, get_challenges
from services.challenge.solve_challenge import submit_for_grading
from schema.challenge import ChallengeBase, ChallengeResponse, DifficultyLevel, ChallengeSubmissionResponse, ChallengeSubmissionRequest

challenge_router = APIRouter(prefix="/api/v1", tags=["Code Challenge"])

@challenge_router.get("/challenges", response_model=List[ChallengeBase])
async def get_challenge_list(db:AsyncSession=Depends(get_db),
                             difficulty:Optional[DifficultyLevel]=Query(None),
                             page:int=Query(1, ge=1, description="페이지 수"),
                             size:int=Query(20, ge=1, le=100, description="페이지 당 문제 수")):
    skip = (page - 1) * size
    challenges = await get_challenges(db=db,
                                      difficulty=difficulty,
                                      skip=skip,
                                      limit=size)
    
    return challenges

@challenge_router.get("/challenge/{problem_id}", response_model=ChallengeResponse)
async def get_challenge_detail(problem_id:int=Path(...),
                               db:AsyncSession=Depends(get_db)):
    
    challenge = await get_challenge_by_id(db=db, problem_id=problem_id)
    if not challenge:
        return HTTPException(
            status_code=404,
            detail="Challenge not found"
        )
    return challenge

@challenge_router.post("/challenge/{problem_id}/submit", response_model=ChallengeSubmissionResponse)
async def submit_challenge_solution(problem_id:int,
                                    submission_data:ChallengeSubmissionRequest):
    grading_result = await submit_for_grading(problem_id=problem_id, 
                                              submission_data=submission_data)
    return grading_result