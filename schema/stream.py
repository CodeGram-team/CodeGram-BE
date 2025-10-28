from pydantic import BaseModel
from typing import Optional

class StreamRequest(BaseModel):
    language:str
    code:str

class StreamResponse(BaseModel):
    job_id:str
    websocket_url:str

class StreamMessage(BaseModel):
    """
    Message schema to be transmitted via WebSocket
    """ 
    type:str # stdout / stderr / status 
    data:Optional[str] = None
    status:Optional[str] = None