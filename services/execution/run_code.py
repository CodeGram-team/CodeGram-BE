import uuid
from redis.asyncio import Redis
import json
from db.rmq import rmq_client
from schema.stream import StreamRequest

"""
# TODO: Redis Pub/Sub에서 RabbitMQ RPC pattern으로 교체 예정
결과를 스트리밍 할 것인지, 한 번에 처리하여 보여줄 것인지 결정할 것
""" 
async def reverse_streamin_job(request:StreamRequest, redis:Redis)->str:
    
    job_id = str(uuid.uuid4())
    await redis.set(f"job_info:{job_id}", json.dumps(request.model_dump()), ex=60)
    
    return job_id

async def code_execution(job_id:str, redis:Redis):
    """
    사용자 게시글 올리기 전 코드 실행할 수 있는 함수
    실시간 스트리밍 
    Args:
    - request:
    - redis:
    Returns:
    - 
    """
    job_info_str = await redis.get(f"job_info:{job_id}")
    if not job_info_str:
        print(f"Job info not found for job_id:{job_id}")
        return
    
    job_info = json.loads(job_info_str)
    response_channel = f"stream:{job_id}"
    
    job_data = {
        "job_id" : job_id,
        "language" : job_info["language"],
        "code" : job_info["code"],
        "response_channel" : response_channel,
        "stream" : True
    }
    await rmq_client.publish_message(queue_name="code_execution_queue", message_body=job_data)