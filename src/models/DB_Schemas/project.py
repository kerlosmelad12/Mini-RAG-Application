from pydantic import BaseModel,Field,validator
from typing import Optional
from bson.Objectid import Objectid

class Project(BaseModel):
    _id: Optional[Objectid]
    project_id: str = Field(...,min_length=1)



    @validator("project_id")
    def validate_project_id(cls,value):
        if not value.isalnum():
            raise ValueError("project id must be alphanumeric")
        return value
    
    # to ignore any not commen datatypes for pydantic
    class Config :
        arbitrary_types_allowed=True
