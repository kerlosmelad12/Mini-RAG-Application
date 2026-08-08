from pydantic import BaseModel
from typing import Optional
class Processrequest(BaseModel):
    file_id: str=None
    chunk_size: Optional[int]=51200
    chunk_overlap:Optional[int]=20
    do_reset: Optional[int]=0



