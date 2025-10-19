from typing import Dict, Any
import uuid
from schema.challenge import ChallengeSubmissionRequest
from db.rmq import rmq_client

# TODO: 사용자 정보(user.id)도 같이 보내도록 추가할 것
async def submit_for_grading(problem_id:int,
                             submission_data:ChallengeSubmissionRequest) -> Dict[str, Any]:
    submission_id = str(uuid.uuid4())
    job_data = {
        "submission_id" : submission_id,
        "problem_id" : problem_id,
        "language" : submission_data.language,
        "code" : submission_data.code
    }
    result = await rmq_client.rpc_call(queue_name="code_challenge_queue", message_body=job_data)
    
    return result

