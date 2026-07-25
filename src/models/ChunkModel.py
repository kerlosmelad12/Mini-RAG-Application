from .DataBaseModel import DataBaseModel
from .DataBaseModel import DataBaseModel
from .enums import CollectionValues
from .DB_Schemas.data import DataChunk
from bson.objectid import ObjectId
from pymongo import InsertOne

class ChunkModel(DataBaseModel):

    def __init__(self, db_client):
        super().__init__(db_client)
        self.chunkdata_collection=db_client[CollectionValues.DATACHUNKS_COLLECTION_NAME.value]


    @classmethod
    async def create_instance(cls,db_client:object):
        instance=cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collections=await self.db_client.list_collection_names()
        if CollectionValues.DATACHUNKS_COLLECTION_NAME.value not in all_collections:
          self.chunkdata_collection=self.db_client[CollectionValues.DATACHUNKS_COLLECTION_NAME.value]
          indexes=DataChunk.get_indexes()
          for index in indexes:
                await self.chunkdata_collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )


    async def insert_chunck(self,chunk:DataChunk):
        result= await self.chunkdata_collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True))

        chunk.id=result.inserted_id  
        # Here will i get error because in pydantic schema treat with _id as a private

        return chunk
    

    
    async def get_chunk(self,id:str):
        result =await self.chunkdata_collection.find_one({
            "_id":ObjectId(id)
            })
        if result is None:
            return None

        return DataChunk(**result)

    async def get_chunks_by_projectid(self,project_id:str,page_no:int=1,page_size:int=50):
       
       result=await self.chunkdata_collection.find({
          
          "chunk_project_id":ObjectId(project_id) if isinstance(project_id,str) else project_id
                }).skip(
                    (page_no-1) * page_size
                ).limit(page_size).to_list(length=None)


       return [DataChunk(**record) for record in result]

    

    async def insert_many_chunks(self, chunks: list, batch_size: int = 100):
       total_inserted = 0
       for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        operations = [
            InsertOne(chunk.dict(by_alias=True, exclude_unset=True))
            for chunk in batch
        ]
        result = await self.chunkdata_collection.bulk_write(operations)
        total_inserted += len(operations)

       return total_inserted
    

    
    async def delete_chunks_by_project_id(self,project_id:str):
     
     result= await self.chunkdata_collection.delete_many({"chunk_project_id":project_id})

     return result.deleted_count



    

