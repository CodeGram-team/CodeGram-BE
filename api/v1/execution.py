from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from db.redis import get_redis_client
from services.execution.run_code import code_execution
from schema.execution import CodeExecutionRequest, CodeExecutionResponse

execution_router = APIRouter(prefix="/api/v1")

@execution_router.post("/execution", response_model=CodeExecutionResponse)
async def run_code(request:CodeExecutionRequest, 
                   redis:Redis=Depends(get_redis_client)):
    return await code_execution(request=request, redis=redis)