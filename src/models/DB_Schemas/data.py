from pydantic import BaseModel,Field,validator
from typing import Optional
from bson.Objectid import Objectid

class DataChunk(BaseModel):
    _id: Optional[Objectid]
    chunk_text: str= Field(...,min_length=1)
    chunk_metadata: dict 
    chunk_order: int =Field(...,gt=0)
    chunk_project_id: Objectid



    
    # to ignore any not commen datatypes for pydantic
    class Config :
        arbitrary_types_allowed=True
