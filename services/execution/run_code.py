import uuid
from redis.asyncio import Redis
import asyncio
import json
from db.rmq import rmq_client
from schema.execution import CodeExecutionRequest, CodeExecutionResponse

async def code_execution(request:CodeExecutionRequest, redis:Redis)->CodeExecutionResponse:
    """
    사용자 게시글 올리기 전 코드 실행할 수 있는 함수
    """
    job_id = str(uuid.uuid4())
    response_channel = f"result:{job_id}"
    job_data = {
        "job_id" : job_id,
        "language" : request.language,
        "code" : request.code,
        "response_channel" : response_channel
    }
    # STEP 1. 결과를 수신할 임시 채널 구독 
    pubsub = redis.pubsub()
    await pubsub.subscribe(response_channel)
    
    # STEP 2. RabbitMQ 작업 큐에 코드 실행 요청 발행
    await rmq_client.publish_message("code_execution_queue", message_body=job_data)
    
    try:
        async with asyncio.timeout(10):
            async for message in pubsub.listen():
                if message["type"] == "message":
                    result_data = json.loads(message["data"])
                    return CodeExecutionResponse(**result_data)
    except asyncio.TimeoutError:
        return CodeExecutionResponse(
            status="error", stdout="", stderr="Execution timed out while wating for result", execution_time=10.0
        )
    finally:
        await pubsub.unsubscribe(response_channel)