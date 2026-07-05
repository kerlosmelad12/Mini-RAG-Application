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



    

