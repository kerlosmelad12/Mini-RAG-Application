from .DataBaseModel import DataBaseModel
from .DB_Schemas.minirag.schemes.data import DataChunk
from sqlalchemy.future import select
from sqlalchemy import func,delete
from bson.objectid import ObjectId
from sqlalchemy.sql import text as sql_text

class ChunkModel(DataBaseModel):

    def __init__(self, db_client):
        super().__init__(db_client)
        self.db_client=db_client


    @classmethod
    async def create_instance(cls,db_client:object):
        instance=cls(db_client)
        return instance

    
    async def insert_chunck(self,chunk:DataChunk):
       async with self.db_client() as session:
                   async with session.begin():
                       session.add(chunk)
                   await session.commit()
                   await session.refresh(chunk)
               
       return chunk
     
    

    
    async def get_chunk(self,id:int):

        async with self.db_client() as session:
            async with session.begin():
                query= select(DataChunk).where(DataChunk.chunk_id==id)
                result= await session.execute(query)
                chunk=result.scalar_one_or_none()

                if chunk is None:
                    return None

                
                return chunk



            
    async def get_chunks_by_projectid(self,project_id:int,page_no:int=1,page_size:int=50):
       
       async with self.db_client() as session:
            stmt = select(DataChunk).where(DataChunk.chunk_project_id == project_id).offset((page_no - 1) * page_size).limit(page_size)
            result = await session.execute(stmt)
            records = result.scalars().all()


       return records

    

    async def insert_many_chunks(self, chunks: list, batch_size: int = 100):


        async with self.db_client() as session:
            async with session.begin():
                for i in range(0, len(chunks), batch_size):
                    batch = chunks[i:i+batch_size]
                    session.add_all(batch)
            await session.commit()
        return len(chunks)
    

    
    async def delete_chunks_by_project_id(self,project_id:int):
     
        async with self.db_client() as session:
            stmt = delete(DataChunk).where(DataChunk.chunk_project_id == project_id)
            result = await session.execute(stmt)
            await session.commit()
        return result.rowcount


    async def get_total_chunks_count(self, project_id: ObjectId):
        total_count = 0
        async with self.db_client() as session:
            count_sql = select(func.count(DataChunk.chunk_id)).where(DataChunk.chunk_project_id == project_id)
            records_count = await session.execute(count_sql)
            total_count = records_count.scalar()
        
        return total_count


    async def get_dominant_language(self, project_id: int) -> str:
      
        async with self.db_client() as session:
            async with session.begin():
                query = sql_text("""
                    SELECT chunk_metadata->>'language' as lang, COUNT(*) as cnt
                    FROM datachunks
                    WHERE chunk_project_id = :project_id
                      AND chunk_metadata->>'language' IS NOT NULL
                    GROUP BY chunk_metadata->>'language'
                    ORDER BY cnt DESC
                    LIMIT 1
                """)
                result = await session.execute(query, {"project_id": project_id})
                row = result.fetchone()

        return row.lang if row else None




    

