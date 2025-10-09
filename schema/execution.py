from pydantic import BaseModel

class CodeExecutionRequest(BaseModel):
    language:str
    code:str

class CodeExecutionResponse(BaseModel):
    status: str
    stdout: str
    stderr: str
    execution_time: float