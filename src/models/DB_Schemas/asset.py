from pydantic import BaseModel,Field,validator
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime

class Asset(BaseModel):
    id: Optional[ObjectId]=Field(None, alias="_id") # toto  solve the problem about private _id
    asset_type:str=Field(...,min_lenght=1)
    asset_name:str=Field(...,min_lenght=1)
    asset_size:int=Field(ge=0,default=None)
    asset_pused_at:datetime=Field(default=datetime.utcnow)
    asset_config:dict=Field(default=None)
    asset_project_id:ObjectId


     #Create index on project_id
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key":[
                    ("asset_project_id",1)
                ],
                "name":"asset_project_id_index_1",
                "unique":False
            },
               {
                "key":[
                    ("asset_project_id",1),
                    ("asset_name",1)
                ],
                "name":"asset_project_id_asset_name_index_1",
                "unique":True
            }

        ]


    
    # to ignore any not commen datatypes for pydantic
    class Config :
        arbitrary_types_allowed=True
        allow_population_by_field_name = True

    
