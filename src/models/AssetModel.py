from .DataBaseModel import DataBaseModel
from .enums import CollectionValues
from .DB_Schemas.asset import Asset
from bson.objectid import ObjectId

class AssetModel(DataBaseModel):

    def __init__(self, db_client):
        super().__init__(db_client)
        self.asset_collection=db_client[CollectionValues.ASSET_COLLECTION_NAME.value] 

    
    @classmethod
    async def create_instance(cls,db_client:object):
        instance=cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collections=await self.db_client.list_collection_names()
        if CollectionValues.ASSET_COLLECTION_NAME.value not in all_collections:
          self.asset_collection=self.db_client[CollectionValues.ASSET_COLLECTION_NAME.value] 
          indexes=Asset.get_indexes()
          for index in indexes:
                await self.asset_collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )

    
    async def get_asset(self,asset_project_id:str,assest_name:str):
      result=await self.asset_collection.find({"asset_name":assest_name,
                                    "asset_project_id":ObjectId(asset_project_id)})
      
      if result is None:
          None
     
      
      return Asset(**result)
    
    async def insert_asset(self,asset:Asset):
        result= await self.asset_collection.insert_one(asset.dict(by_alias=True, exclude_unset=True))

        asset.id=result.inserted_id  
        # Here will i get error because in pydantic schema treat with _id as a private

        return asset    
    
    async def get_all_project_assets(self,asset_project_id:str,asset_type:str):
        record= await self.asset_collection.find({
              "asset_project_id":ObjectId(asset_project_id) if isinstance(asset_project_id,str) else asset_project_id,
              "asset_type":asset_type
                                                   }).to_list(length=None)
        return [Asset(**record) for record in record]

    
          

    

      
          
