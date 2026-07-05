from pydantic import BaseModel,Field,validator
from typing import Optional
from bson.objectid import ObjectId

class Project(BaseModel):
    id: Optional[ObjectId]=Field(None, alias="_id") # toto  solve the problem about private _id
    project_id: str = Field(...,min_length=1)



    @validator("project_id")
    def validate_project_id(cls,value):
        if not value.isalnum():
            raise ValueError("project id must be alphanumeric")
        return value
    
    # to ignore any not commen datatypes for pydantic
    class Config :
        arbitrary_types_allowed=True
        allow_population_by_field_name = True
