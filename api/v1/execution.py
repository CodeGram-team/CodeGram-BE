from fastapi import APIRouter, Depends
import os, uuid
from dotenv import load_dotenv
from core.token import Token
from utils.current_user import get_current_user
from schema.stream import StreamRequest, StreamResponse
load_dotenv()

execution_router = APIRouter(prefix="/api/v1", tags=["Code Execution"])
token_inst = Token()
WORKER_SERVER=os.getenv("WORKER_SERVER")

@execution_router.post("/stream", response_model=StreamResponse)
async def run_code_stream(request:StreamRequest):
    """
    코드 실행 시작 -> 결과를 수신할 WebSocket URL 반환
    """
    job_id = str(uuid.uuid4())
    websocket_url = f"{WORKER_SERVER}/ws/worker/{request.language}?job_id={job_id}"
    
    return StreamResponse(job_id=job_id, websocket_url=websocket_url)